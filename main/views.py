from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.db.models import Q, F
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json

from .models import Announcement, Collection, User, Agency, Photo
from .forms import (
    UserRegistrationForm, PhoneLoginForm, AnnouncementForm, 
    CollectionForm, SearchForm
)
from .services import (
    UserService, AnnouncementService, CollectionService, 
    AgencyService, PhotoService, UserSessionService, PageViewService
)
from .utils import (
    log_login, log_logout, log_announcement_action, 
    log_collection_action, log_search_action, log_filter_action,
    log_user_activity
)


def agency_autocomplete(request):
    """AJAX endpoint for agency autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if len(query) >= 1:  # Начинаем поиск с первого символа
            agencies = Agency.objects.filter(
                name__icontains=query
            )[:10]  # Ограничиваем результат 10 агентствами
            
            suggestions = []
            for agency in agencies:
                suggestions.append({
                    'id': agency.id,
                    'name': agency.name,
                    'users_count': agency.users.count()  # Количество пользователей в агентстве
                })
            
            return JsonResponse({
                'suggestions': suggestions,
                'query': query
            })
    
    return JsonResponse({'suggestions': [], 'query': ''})


def complex_autocomplete(request):
    """AJAX endpoint for complex name autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if len(query) >= 1:  # Начинаем поиск с первого символа
            from .models import Address
            # Получаем уникальные названия жилых комплексов
            complexes = Address.objects.filter(
                complex_name__icontains=query,
                complex_name__isnull=False
            ).exclude(
                complex_name__exact=''
            ).values_list('complex_name', flat=True).distinct()[:10]
            
            suggestions = []
            for complex_name in complexes:
                suggestions.append({
                    'name': complex_name,
                })
            
            return JsonResponse({
                'suggestions': suggestions,
                'query': query
            })
    
    return JsonResponse({'suggestions': [], 'query': ''})


class CustomLoginView(View):
    """Custom login view using phone authentication"""
    template_name = 'main/login.html'
    form_class = PhoneLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('announcement_list')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST, request=request)
        
        if form.is_valid():
            # User is already authenticated by the form's clean method
            user = form.get_user()
            
            if user:
                user.backend = 'main.auth_backends.PhoneAuthBackend'
                login(request, user)
                
                # Log user session
                UserSessionService.create_session(user, request.session.session_key)
                
                # Log user login activity
                log_login(user, request)
                
                # Check if this is first login
                if user.is_first_login:
                    user.is_first_login = False
                    user.save()
                    messages.success(request, f'Добро пожаловать в ProAgentAstana, {user.first_name}! Это ваш первый вход в систему.')
                    messages.info(request, 'Начните с добавления своего первого объявления о недвижимости!')
                else:
                    messages.success(request, f'С возвращением, {user.first_name}!')
                
                return redirect('announcement_list')
            else:
                messages.error(request, 'Authentication failed.')
        else:
            # Form validation failed - errors are already displayed by the form
            pass
        
        return render(request, self.template_name, {'form': form})


class UserRegistrationView(View):
    """User registration view"""
    template_name = 'main/user_register.html'
    form_class = UserRegistrationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('announcement_list')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            # Сначала валидируем и подготавливаем все данные
            try:
                agency_name = form.cleaned_data['agency_name']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone = form.cleaned_data['phone']
                password = form.cleaned_data['password']
                email = form.cleaned_data.get('email', '')
                additional_phone = form.cleaned_data.get('additional_phone', '')
                whatsapp_phone = form.cleaned_data.get('whatsapp_phone', '')
                
                # Проверяем, что пользователь с таким телефоном не существует
                if User.objects.filter(phone=phone).exists():
                    messages.error(request, 'User with this phone number already exists.')
                    return render(request, self.template_name, {'form': form})
                
                # Получаем или создаем агентство по названию
                agency, agency_created = Agency.objects.get_or_create(name=agency_name)
                
                # Теперь создаем пользователя
                user = UserService.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    password=password,
                    agency=agency,
                    email=email,
                    additional_phone=additional_phone,
                    whatsapp_phone=whatsapp_phone,
                )
                
                # Авторизуем пользователя с указанием backend
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                UserSessionService.create_session(user, request.session.session_key)
                
                # Показываем сообщение об успехе
                if agency_created:
                    messages.success(request, f'Registration successful! Welcome to ProAgentAstana! New agency "{agency_name}" has been created.')
                else:
                    messages.success(request, 'Registration successful! Welcome to ProAgentAstana!')
                return redirect('announcement_list')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                # Логируем ошибку для отладки
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'User registration error: {e}', exc_info=True)
        else:
            # Форма не валидна
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, self.template_name, {'form': form})


class AnnouncementListView(ListView):
    """List view for announcements"""
    model = Announcement
    template_name = 'main/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 12

    def get_queryset(self):
        queryset = AnnouncementService.get_all_announcements()
        
        # Handle search with new advanced filters
        form = SearchForm(self.request.GET)
        if form.is_valid():
            # Количество комнат (множественный выбор)
            rooms_count = form.cleaned_data.get('rooms_count')
            if rooms_count:
                room_filters = Q()
                for room in rooms_count:
                    if room == '5+':
                        room_filters |= Q(rooms_count__gte=5)
                    else:
                        room_filters |= Q(rooms_count=int(room))
                queryset = queryset.filter(room_filters)
            
            # Цена
            price_from = form.cleaned_data.get('price_from')
            price_to = form.cleaned_data.get('price_to')
            if price_from:
                queryset = queryset.filter(price__gte=price_from)
            if price_to:
                queryset = queryset.filter(price__lte=price_to)
            
            # Цена за м² (вычисляемое поле)
            price_per_sqm_from = form.cleaned_data.get('price_per_sqm_from')
            price_per_sqm_to = form.cleaned_data.get('price_per_sqm_to')
            if price_per_sqm_from:
                # price / area >= price_per_sqm_from
                # price >= price_per_sqm_from * area
                queryset = queryset.extra(
                    where=["price / area >= %s"],
                    params=[price_per_sqm_from]
                )
            if price_per_sqm_to:
                # price / area <= price_per_sqm_to
                queryset = queryset.extra(
                    where=["price / area <= %s"],
                    params=[price_per_sqm_to]
                )
            
            # Микрорайон
            microdistrict = form.cleaned_data.get('microdistrict')
            if microdistrict:
                queryset = queryset.filter(address__microdistrict=microdistrict)
            
            # Тип дома
            building_type = form.cleaned_data.get('building_type')
            if building_type:
                queryset = queryset.filter(building_type=building_type)
            
            # Год постройки
            year_built_from = form.cleaned_data.get('year_built_from')
            year_built_to = form.cleaned_data.get('year_built_to')
            if year_built_from:
                queryset = queryset.filter(year_built__gte=year_built_from)
            if year_built_to:
                queryset = queryset.filter(year_built__lte=year_built_to)
            
            # Жилой комплекс
            complex_name = form.cleaned_data.get('complex_name')
            if complex_name:
                queryset = queryset.filter(address__complex_name__exact=complex_name)
            
            # Площадь
            area_from = form.cleaned_data.get('area_from')
            area_to = form.cleaned_data.get('area_to')
            if area_from:
                queryset = queryset.filter(area__gte=area_from)
            if area_to:
                queryset = queryset.filter(area__lte=area_to)
            
            # Этаж
            floor_from = form.cleaned_data.get('floor_from')
            floor_to = form.cleaned_data.get('floor_to')
            if floor_from:
                queryset = queryset.filter(floor__gte=floor_from)
            if floor_to:
                queryset = queryset.filter(floor__lte=floor_to)
            
            # Не первый этаж
            not_first_floor = form.cleaned_data.get('not_first_floor')
            if not_first_floor:
                queryset = queryset.filter(floor__gt=1)
            
            # Не последний этаж
            not_last_floor = form.cleaned_data.get('not_last_floor')
            if not_last_floor:
                queryset = queryset.exclude(floor=F('total_floors'))
            
            # Только новостройки
            is_new_building = form.cleaned_data.get('is_new_building')
            if is_new_building:
                queryset = queryset.filter(is_new_building=True)
            
            # Только предложения от агентства
            agency_only = form.cleaned_data.get('agency_only')
            if agency_only:
                # Показываем только объявления где партнер дополнительно платит вознаграждение
                # Это третий вариант комиссии: 'buyer' - "Я беру с продавца, вы - с покупателя и я дополнительно доплачиваю вам"
                queryset = queryset.filter(commission_type='buyer')
            
            # Фильтр по агентству
            agency = form.cleaned_data.get('agency')
            if agency:
                queryset = queryset.filter(user__agency=agency)
            
            # Фильтр по опорным точкам
            landmarks = form.cleaned_data.get('landmarks')
            if landmarks:
                queryset = queryset.filter(landmarks__in=landmarks)
            
            # Log search/filter activity
            if self.request.user.is_authenticated:
                search_params = {}
                for key, value in form.cleaned_data.items():
                    if value:
                        search_params[key] = str(value)
                
                if search_params:
                    if any(key in search_params for key in ['rooms_count', 'price_from', 'price_to', 'microdistrict', 'building_type', 'complex_name', 'area_from', 'area_to']):
                        log_filter_action(self.request.user, search_params, self.request)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        
        # Добавляем информацию о коллекциях для каждого объявления
        if self.request.user.is_authenticated:
            announcements = context['announcements']
            for announcement in announcements:
                announcement.user_collections = CollectionService.get_announcement_collections(announcement, self.request.user)
        
        return context


class AnnouncementDetailView(DetailView):
    """Detail view for announcements"""
    model = Announcement
    template_name = 'main/announcement_detail.html'
    context_object_name = 'announcement'

    def get_object(self):
        # Используем сервис для получения одного объявления
        announcement = AnnouncementService.get_announcement_by_id(self.kwargs['pk'])
        if announcement is None:
            raise Http404("Announcement does not exist")
        return announcement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем фото в контекст
        context['photos'] = self.object.photos.all()
        
        # Добавляем коллекции пользователя для кнопки "Добавить в коллекцию"
        if self.request.user.is_authenticated:
            context['user_collections'] = CollectionService.get_user_collections(self.request.user)
            # Добавляем информацию о том, в каких коллекциях уже находится объявление
            context['announcement_collections'] = CollectionService.get_announcement_collections(self.object, self.request.user)
        
        # Log announcement view
        if self.request.user.is_authenticated:
            log_announcement_action(
                self.request.user, 
                'view_announcement', 
                self.object, 
                self.request
            )
        
        return context


class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    """Create view for announcements"""
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'main/announcement_form.html'

    def form_valid(self, form):
        try:
            # Validate photo file sizes first
            photos = self.request.FILES.getlist('photos')
            max_file_size = 10 * 1024 * 1024  # 10MB
            
            for photo in photos:
                if photo.size > max_file_size:
                    messages.error(self.request, f'Файл {photo.name} слишком большой. Максимальный размер: 10MB')
                    return self.form_invalid(form)
                
                if not photo.content_type.startswith('image/'):
                    messages.error(self.request, f'Файл {photo.name} должен быть изображением')
                    return self.form_invalid(form)
            
            # Set the user
            form.instance.user = self.request.user
            
            # Check if the archive button was pressed
            if '_archive' in self.request.POST:
                form.instance.is_archived = True
            
            # Save the announcement using the form's save method (handles ManyToMany fields correctly)
            announcement = form.save()
            
            # Handle photo uploads with error handling
            photo_objects = []
            for i, photo in enumerate(photos):
                try:
                    photo_obj = PhotoService.save_announcement_photo(announcement, photo)
                    photo_objects.append(photo_obj)
                except Exception as e:
                    messages.warning(self.request, f'Ошибка загрузки фото {photo.name}: {str(e)}')
                    continue
            
            # Handle setting main photo
            main_photo_id = self.request.POST.get('main_photo_id')
            if main_photo_id and main_photo_id.startswith('new_'):
                # This is a new photo
                try:
                    index = int(main_photo_id.replace('new_', ''))
                    if index < len(photo_objects):
                        photo_objects[index].is_main = True
                        photo_objects[index].save()
                except (ValueError, IndexError):
                    pass
            elif photo_objects:
                # If no main photo is selected, make the first one main
                photo_objects[0].is_main = True
                photo_objects[0].save()
            
            # Log announcement creation
            log_announcement_action(
                self.request.user, 
                'create_announcement', 
                announcement, 
                self.request
            )
            
            messages.success(self.request, 'Объявление создано успешно!')
            return redirect('announcement_detail', pk=announcement.pk)
            
        except Exception as e:
            # Handle database errors
            import traceback
            error_message = str(e)
            
            # Check for specific database errors
            if 'cursor' in error_message.lower() and 'does not exist' in error_message.lower():
                messages.error(self.request, 'Ошибка подключения к базе данных. Попробуйте еще раз.')
            elif 'too large' in error_message.lower() or '413' in error_message:
                messages.error(self.request, 'Загружаемые файлы слишком большие. Уменьшите размер изображений.')
            else:
                messages.error(self.request, f'Ошибка при создании объявления: {error_message}')
            
            # Log the full error for debugging
            print(f"Announcement creation error: {traceback.format_exc()}")
            return self.form_invalid(form)


class AnnouncementUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for announcements"""
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'main/announcement_form.html'

    def get_queryset(self):
        return Announcement.objects.filter(user=self.request.user)

    def form_valid(self, form):
        try:
            # Update address
            address_data = form.get_address_data()
            for field, value in address_data.items():
                setattr(self.object.address, field, value)
            self.object.address.save()
            
            # Handle new photo uploads
            photos = self.request.FILES.getlist('photos')
            new_photos = []
            for photo in photos:
                photo_obj = PhotoService.save_announcement_photo(self.object, photo)
                new_photos.append(photo_obj)
            
            # Handle setting main photo
            main_photo_id = self.request.POST.get('main_photo_id')
            if main_photo_id:
                # Сначала убираем отметку главного со всех фото
                self.object.photos.update(is_main=False)
                
                if main_photo_id.startswith('new_'):
                    # Это новое фото
                    index = int(main_photo_id.replace('new_', ''))
                    if index < len(new_photos):
                        new_photos[index].is_main = True
                        new_photos[index].save()
                else:
                    # Это существующее фото
                    try:
                        photo = self.object.photos.get(id=main_photo_id)
                        photo.is_main = True
                        photo.save()
                    except Photo.DoesNotExist:
                        pass
            
            # Log announcement update
            log_announcement_action(
                self.request.user, 
                'edit_announcement', 
                self.object, 
                self.request
            )
            
            messages.success(self.request, 'Announcement updated successfully!')
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error updating announcement: {str(e)}')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('announcement_detail', kwargs={'pk': self.object.pk})


class AnnouncementDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for announcements"""
    model = Announcement
    template_name = 'main/announcement_confirm_delete.html'
    success_url = reverse_lazy('announcement_list')

    def get_queryset(self):
        return Announcement.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Log announcement deletion before actually deleting
        announcement = self.get_object()
        log_announcement_action(
            request.user, 
            'delete_announcement', 
            announcement, 
            request
        )
        
        messages.success(request, 'Announcement deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CollectionListView(LoginRequiredMixin, ListView):
    """List view for collections"""
    model = Collection
    template_name = 'main/collection_list.html'
    context_object_name = 'collections'
    paginate_by = 10

    def get_queryset(self):
        return CollectionService.get_user_collections(self.request.user)


class CollectionDetailView(LoginRequiredMixin, DetailView):
    """Detail view for collections"""
    model = Collection
    template_name = 'main/collection_detail.html'
    context_object_name = 'collection'

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active and archived announcements separately
        active_announcements = CollectionService.get_active_collection_announcements(self.object)
        archived_announcements = CollectionService.get_archived_collection_announcements(self.object)
        
        context['active_announcements'] = active_announcements
        context['archived_announcements'] = archived_announcements
        context['total_announcements'] = active_announcements.count() + archived_announcements.count()
        
        return context


class CollectionCreateView(LoginRequiredMixin, CreateView):
    """Create view for collections"""
    model = Collection
    form_class = CollectionForm
    template_name = 'main/collection_form.html'

    def form_valid(self, form):
        collection = CollectionService.create_collection(
            user=self.request.user,
            name=form.cleaned_data['name']
        )
        
        # Log collection creation
        log_collection_action(
            self.request.user, 
            'create_collection', 
            collection, 
            self.request
        )
        
        messages.success(self.request, 'Collection created successfully!')
        return redirect('collection_detail', pk=collection.pk)


class CollectionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for collections"""
    model = Collection
    template_name = 'main/collection_confirm_delete.html'
    success_url = reverse_lazy('collection_list')

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Collection deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AccountView(LoginRequiredMixin, View):
    """User account view"""
    template_name = 'main/account.html'

    def get(self, request):
        archived_announcements = AnnouncementService.get_archived_user_announcements(request.user)
        user_announcements = AnnouncementService.get_user_announcements(request.user)
        user_collections = CollectionService.get_user_collections(request.user)
        total_announcements = user_announcements.count()
        total_collections = user_collections.count()
        
        from .forms import ChangeAgencyForm, ChangePasswordForm
        change_agency_form = ChangeAgencyForm(user=request.user)
        change_password_form = ChangePasswordForm(user=request.user)
        
        context = {
            'user': request.user,
            'archived_announcements': archived_announcements,
            'user_announcements': user_announcements,
            'user_collections': user_collections,
            'total_announcements': total_announcements,
            'total_collections': total_collections,
            'change_agency_form': change_agency_form,
            'change_password_form': change_password_form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        from .forms import ChangeAgencyForm, ChangePasswordForm
        from .utils import log_user_activity
        
        if 'change_agency' in request.POST:
            change_agency_form = ChangeAgencyForm(request.POST, user=request.user)
            change_password_form = ChangePasswordForm(user=request.user)
            
            if change_agency_form.is_valid():
                try:
                    # Сохраняем изменения агентства
                    result = change_agency_form.save(request.user)
                    
                    # Логируем изменение агентства
                    log_user_activity(
                        user=request.user,
                        action_type='agency_changed',
                        description=f'Агентство изменено с "{result["old_agency"].name}" на "{result["agency"].name}"',
                        request=request,
                        is_successful=True
                    )
                    
                    # Очищаем флаг уведомления в сессии
                    if 'agency_notification_shown' in request.session:
                        del request.session['agency_notification_shown']
                    
                    # Показываем сообщение об успехе
                    if result['created']:
                        messages.success(
                            request,
                            f'Агентство успешно изменено на "{result["agency"].name}". '
                            f'Новое агентство было создано.'
                        )
                    else:
                        messages.success(
                            request,
                            f'Агентство успешно изменено на "{result["agency"].name}".'
                        )
                    
                    return redirect('account')
                    
                except Exception as e:
                    # Логируем ошибку
                    log_user_activity(
                        user=request.user,
                        action_type='agency_changed',
                        description=f'Ошибка при изменении агентства: {str(e)}',
                        request=request,
                        is_successful=False,
                        error_message=str(e)
                    )
                    messages.error(request, f'Ошибка при изменении агентства: {str(e)}')
            else:
                # Форма не валидна
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        
        elif 'change_password' in request.POST:
            change_password_form = ChangePasswordForm(request.user, request.POST)
            change_agency_form = ChangeAgencyForm(user=request.user)
            if change_password_form.is_valid():
                change_password_form.save()
                messages.success(request, 'Пароль успешно изменён!')
                return redirect('account')
            else:
                messages.error(request, 'Проверьте правильность заполнения формы смены пароля.')
            context = {
                'user': request.user,
                'archived_announcements': AnnouncementService.get_archived_user_announcements(request.user),
                'user_announcements': AnnouncementService.get_user_announcements(request.user),
                'user_collections': CollectionService.get_user_collections(request.user),
                'total_announcements': AnnouncementService.get_user_announcements(request.user).count(),
                'total_collections': CollectionService.get_user_collections(request.user).count(),
                'change_agency_form': change_agency_form,
                'change_password_form': change_password_form,
            }
            return render(request, self.template_name, context)
        else:
            return self.get(request)


# AJAX Views for collection management
@login_required
def add_to_collection(request):
    """AJAX view to add announcement to collection"""
    if request.method == 'POST':
        announcement_id = request.POST.get('announcement_id')
        collection_id = request.POST.get('collection_id')
        
        try:
            announcement = get_object_or_404(Announcement, pk=announcement_id)
            collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
            
            item, created = CollectionService.add_announcement_to_collection(collection, announcement)
            
            if created:
                # Log adding to collection
                log_collection_action(
                    request.user, 
                    'add_to_collection', 
                    collection, 
                    request, 
                    announcement
                )
                return JsonResponse({'success': True, 'message': 'Added to collection'})
            else:
                return JsonResponse({'success': False, 'message': 'Already in collection'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def get_announcement_collections(request, announcement_id):
    """AJAX view to get collections that contain this announcement"""
    try:
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        
        # Get collections that contain this announcement for current user
        collections = Collection.objects.filter(
            user=request.user,
            collection_items__announcement=announcement
        ).values('id', 'name')
        
        return JsonResponse({
            'success': True,
            'collections': list(collections)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def remove_from_collection(request):
    """AJAX view to remove announcement from collection"""
    if request.method == 'POST':
        announcement_id = request.POST.get('announcement_id')
        collection_id = request.POST.get('collection_id')
        
        try:
            announcement = get_object_or_404(Announcement, pk=announcement_id)
            collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
            
            success = CollectionService.remove_announcement_from_collection(collection, announcement)
            
            if success:
                # Log removing from collection
                log_collection_action(
                    request.user, 
                    'remove_from_collection', 
                    collection, 
                    request, 
                    announcement
                )
                return JsonResponse({'success': True, 'message': 'Removed from collection'})
            else:
                return JsonResponse({'success': False, 'message': 'Not in collection'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def create_collection_ajax(request):
    """AJAX view to create new collection"""
    if request.method == 'POST':
        collection_name = request.POST.get('collection_name', '').strip()
        
        if not collection_name:
            return JsonResponse({'success': False, 'message': 'Название коллекции не может быть пустым'})
        
        if len(collection_name) > 255:
            return JsonResponse({'success': False, 'message': 'Название коллекции слишком длинное'})
        
        try:
            # Проверяем, нет ли уже такой коллекции у пользователя
            if Collection.objects.filter(user=request.user, name=collection_name).exists():
                return JsonResponse({'success': False, 'message': 'Коллекция с таким названием уже существует'})
            
            # Создаем новую коллекцию
            collection = Collection.objects.create(
                user=request.user,
                name=collection_name
            )
            
            # Log collection creation
            log_collection_action(
                request.user, 
                'create_collection', 
                collection, 
                request
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Коллекция создана успешно',
                'collection': {
                    'id': collection.id,
                    'name': collection.name
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка создания коллекции: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def rename_collection(request, pk):
    """Rename a collection"""
    collection = get_object_or_404(Collection, pk=pk)
    
    # Check if user owns the collection
    if request.user != collection.user:
        return JsonResponse({'success': False, 'message': 'У вас нет прав для переименования этой коллекции.'})
    
    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()
        
        if not new_name:
            return JsonResponse({'success': False, 'message': 'Название коллекции не может быть пустым.'})
        
        if new_name == collection.name:
            return JsonResponse({'success': False, 'message': 'Новое название должно отличаться от текущего.'})
        
        # Check if name already exists for this user
        if Collection.objects.filter(user=request.user, name=new_name).exclude(pk=pk).exists():
            return JsonResponse({'success': False, 'message': 'Коллекция с таким названием уже существует.'})
        
        old_name = collection.name
        collection.name = new_name
        collection.save()
        
        # Log the action
        from .utils import log_user_activity
        log_user_activity(
            user=request.user,
            action_type='edit_collection',
            description=f'Коллекция "{old_name}" переименована в "{new_name}"',
            request=request,
            related_collection=collection,
            is_successful=True
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Коллекция успешно переименована в "{new_name}".'
        })
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос.'})


def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        # Log user logout activity
        log_logout(request.user, request)
        
        # End user session
        UserSessionService.end_session(request.session.session_key)
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def account_delete(request):
    """Delete user account and all related data"""
    if request.method == 'POST':
        user = request.user
        
        # Логируем попытку удаления аккаунта
        print(f"Attempting to delete account for user: {user.phone}")
        
        # Удаляем все объявления пользователя (вместе с фотографиями)
        announcements = Announcement.objects.filter(user=user)
        for announcement in announcements:
            # Удаляем все фотографии объявления
            for photo in announcement.photos.all():
                photo.delete()  # Это также удалит файл из файловой системы
            announcement.delete()
        
        # Удаляем все коллекции пользователя
        collections = Collection.objects.filter(user=user)
        collections.delete()
        
        # Удаляем все фотографии пользователя
        for photo in user.photos.all():
            photo.delete()  # Это также удалит файл из файловой системы
        
        # Завершаем сеанс пользователя
        if hasattr(request, 'session') and request.session.session_key:
            UserSessionService.end_session(request.session.session_key)
        
        # Удаляем пользователя
        user.delete()
        
        # Выходим из системы
        logout(request)
        
        messages.success(request, 'Ваш аккаунт был успешно удален. Спасибо за использование нашего сервиса.')
        return redirect('announcement_list')
    
    # Если не POST запрос, перенаправляем на страницу аккаунта
    return redirect('account')


@login_required
def upload_user_photo(request):
    """AJAX endpoint for uploading user photo"""
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            photo_file = request.FILES['photo']
            
            # Валидация файла
            if photo_file.size > 10 * 1024 * 1024:  # 10MB
                return JsonResponse({'success': False, 'message': 'Файл слишком большой. Максимальный размер: 10MB'})
            
            if not photo_file.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'message': 'Файл должен быть изображением'})
            
            # Удаляем старые фотографии пользователя
            for old_photo in request.user.photos.all():
                old_photo.delete()
            
            # Сохраняем новую фотографию
            new_photo = PhotoService.save_user_photo(request.user, photo_file)
            new_photo.is_main = True
            new_photo.save()
            
            # Логируем загрузку фотографии
            log_user_activity(
                request.user,
                'upload_user_photo',
                f"Загружена новая фотография профиля",
                request=request,
                metadata={'file_name': photo_file.name, 'file_size': photo_file.size}
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Фотография успешно обновлена',
                'photo_url': f"{settings.MEDIA_URL}{new_photo.file_path}"
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка загрузки: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})


@login_required
def archive_announcement(request, pk):
    """Archive an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Check if user owns the announcement
    if request.user != announcement.user:
        messages.error(request, 'У вас нет прав для архивирования этого объявления.')
        return redirect('account')
    
    if request.method == 'POST':
        announcement.is_archived = True
        announcement.save()
        
        # Log the action
        from .utils import log_user_activity
        log_user_activity(
            user=request.user,
            action_type='archive_announcement',
            description=f'Объявление #{announcement.pk} помещено в архив',
            request=request,
            related_announcement=announcement,
            is_successful=True
        )
        
        messages.success(request, 'Объявление помещено в архив.')
        return redirect('account')
    
    return redirect('account')


@login_required
def unarchive_announcement(request, pk):
    """Unarchive an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Check if user owns the announcement
    if request.user != announcement.user:
        messages.error(request, 'У вас нет прав для разархивирования этого объявления.')
        return redirect('account')
    
    if request.method == 'POST':
        announcement.is_archived = False
        announcement.save()
        
        # Log the action
        from .utils import log_user_activity
        log_user_activity(
            user=request.user,
            action_type='unarchive_announcement',
            description=f'Объявление #{announcement.pk} восстановлено из архива',
            request=request,
            related_announcement=announcement,
            is_successful=True
        )
        
        messages.success(request, 'Объявление восстановлено из архива.')
        return redirect('account')
    
    return redirect('account')


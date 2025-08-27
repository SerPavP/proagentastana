from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
import csv
import xlwt
from datetime import datetime
from .models import (
    Agency, User, UserPhoto, Address, Announcement, Photo, 
    Collection, CollectionItem, Tariff, Subscription, 
    UserSession, PageView, Landmark, Microdistrict,
    ResidentialComplex, RepairType, BuildingType, UserActivity
)


# ===== СПРАВОЧНИКИ =====

@admin.register(Microdistrict)
class MicrodistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(ResidentialComplex)
class ResidentialComplexAdmin(admin.ModelAdmin):
    list_display = ['name', 'microdistrict', 'is_active', 'created_at']
    list_filter = ['is_active', 'microdistrict', 'created_at']
    search_fields = ['name', 'microdistrict__name']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(RepairType)
class RepairTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'users_count', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    actions = ['delete_selected_agencies']
    
    def users_count(self, obj):
        return obj.users.count()
    users_count.short_description = 'Количество пользователей'
    
    def delete_selected_agencies(self, request, queryset):
        """Удаление выбранных агентств с переносом пользователей в 'Прочее'"""
        from django.contrib import messages
        
        # Получаем или создаем агентство "Прочее"
        other_agency, created = Agency.objects.get_or_create(
            name='Прочее',
            defaults={'created_at': timezone.now()}
        )
        
        moved_users_count = 0
        deleted_agencies = []
        
        for agency in queryset:
            if agency.name == 'Прочее':
                messages.warning(request, 'Агентство "Прочее" нельзя удалить.')
                continue
                
            # Переносим всех пользователей в агентство "Прочее"
            users_to_move = agency.users.all()
            users_count = users_to_move.count()
            
            if users_count > 0:
                users_to_move.update(agency=other_agency)
                moved_users_count += users_count
                
                # Логируем перенос для каждого пользователя
                for user in users_to_move:
                    from .utils import log_user_activity
                    log_user_activity(
                        user=user,
                        action_type='agency_changed',
                        description=f'Агентство автоматически изменено на "Прочее" из-за удаления агентства "{agency.name}"',
                        request=request,
                        is_successful=True
                    )
            
            deleted_agencies.append(agency.name)
            agency.delete()
        
        if moved_users_count > 0:
            messages.success(
                request, 
                f'Удалено агентств: {len(deleted_agencies)}. '
                f'Перенесено пользователей в "Прочее": {moved_users_count}'
            )
        else:
            messages.success(request, f'Удалено агентств: {len(deleted_agencies)}')
            
        if deleted_agencies:
            messages.info(request, f'Удаленные агентства: {", ".join(deleted_agencies)}')
    
    delete_selected_agencies.short_description = 'Удалить выбранные агентства (с переносом пользователей)'
    
    def delete_model(self, request, obj):
        """Переопределяем удаление одного агентства"""
        if obj.name == 'Прочее':
            messages.warning(request, 'Агентство "Прочее" нельзя удалить.')
            return
            
        # Получаем или создаем агентство "Прочее"
        other_agency, created = Agency.objects.get_or_create(
            name='Прочее',
            defaults={'created_at': timezone.now()}
        )
        
        # Переносим всех пользователей в агентство "Прочее"
        users_to_move = obj.users.all()
        users_count = users_to_move.count()
        
        if users_count > 0:
            users_to_move.update(agency=other_agency)
            
            # Логируем перенос для каждого пользователя
            for user in users_to_move:
                from .utils import log_user_activity
                log_user_activity(
                    user=user,
                    action_type='agency_changed',
                    description=f'Агентство автоматически изменено на "Прочее" из-за удаления агентства "{obj.name}"',
                    request=request,
                    is_successful=True
                )
            
            messages.success(
                request, 
                f'Агентство "{obj.name}" удалено. '
                f'Перенесено пользователей в "Прочее": {users_count}'
            )
        else:
            messages.success(request, f'Агентство "{obj.name}" удалено.')
        
        obj.delete()
        
    def get_actions(self, request):
        """Переопределяем действия для замены стандартного delete_selected"""
        actions = super().get_actions(request)
        # Удаляем стандартное действие удаления
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# ===== ПОЛЬЗОВАТЕЛИ =====

class UserPhotoInline(admin.TabularInline):
    model = UserPhoto
    extra = 0
    fields = ['file_name', 'is_main', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone', 'full_name', 'agency', 'is_active', 'is_superuser', 'last_login', 'created_at', 'password_reset_status']
    list_filter = ['is_active', 'is_superuser', 'is_staff', 'agency', 'created_at']
    search_fields = ['phone', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    actions = ['export_to_excel', 'export_all_users_to_excel', 'export_all_users_to_csv', 'delete_users_with_data', 'make_superuser', 'make_regular_user', 'reset_passwords']
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Контактная информация', {'fields': ('additional_phone', 'whatsapp_phone')}),
        ('Агентство', {'fields': ('agency',)}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'created_at', 'updated_at')}),
        ('Фото пользователя', {
            'fields': ('get_user_photos',),
        }),
        ('Статистика пользователя', {
            'fields': ('get_total_time_on_site', 'get_announcements_count', 'get_archived_count', 
                      'get_collections_count', 'get_photos_count', 'get_activity_count', 'get_activity_link'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'first_name', 'last_name', 'agency', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'get_total_time_on_site', 'get_announcements_count', 
                      'get_archived_count', 'get_collections_count', 'get_photos_count', 'get_activity_count', 
                      'get_activity_link', 'get_user_photos']
    inlines = [UserPhotoInline]
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'ФИО'
    
    def get_total_time_on_site(self, obj):
        """Подсчет общего времени на сайте"""
        sessions = UserSession.objects.filter(user=obj)
        total_duration = sessions.aggregate(total=Sum('duration'))['total']
        if total_duration:
            # Преобразуем timedelta в секунды
            total_seconds = total_duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
        return "0ч 0м"
    get_total_time_on_site.short_description = 'Общее время на сайте'
    
    def get_announcements_count(self, obj):
        """Количество объявлений"""
        total = obj.announcements.count()
        active = obj.announcements.filter(is_archived=False).count()
        return f"{total} (активных: {active})"
    get_announcements_count.short_description = 'Объявления'
    
    def get_archived_count(self, obj):
        """Количество архивированных объявлений"""
        return obj.announcements.filter(is_archived=True).count()
    get_archived_count.short_description = 'Архив'
    
    def get_collections_count(self, obj):
        """Количество подборок"""
        return obj.collections.count()
    get_collections_count.short_description = 'Подборки'
    
    def get_photos_count(self, obj):
        """Количество фотографий"""
        user_photos = obj.photos.count()
        announcement_photos = Photo.objects.filter(announcement__user=obj).count()
        return f"{user_photos + announcement_photos} (профиль: {user_photos}, объявления: {announcement_photos})"
    get_photos_count.short_description = 'Фотографии'
    
    def get_activity_count(self, obj):
        """Количество активности"""
        if hasattr(obj, 'activities'):
            return obj.activities.count()
        return 0
    get_activity_count.short_description = 'Действия'
    
    def get_activity_link(self, obj):
        """Ссылка на все действия пользователя"""
        if hasattr(obj, 'activities'):
            count = obj.activities.count()
            if count > 0:
                return format_html(
                    '<a href="/admin/main/useractivity/?user__id__exact={}" target="_blank">Посмотреть все {} действий</a>',
                    obj.id, count
                )
        return 'Нет действий'
    get_activity_link.short_description = 'Ссылка на действия'
    
    def get_user_photos(self, obj):
        """Отображение фото пользователя"""
        photos = obj.photos.all()
        if photos.exists():
            photo_html = []
            for photo in photos:
                photo_html.append(
                    '<div style="display: inline-block; margin: 5px; text-align: center;">'
                    '<img src="/media/user_photos/{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;">'
                    '<div style="font-size: 11px; color: #666; margin-top: 3px;">{}</div>'
                    '</div>'.format(photo.file_name, 'Главное' if photo.is_main else 'Обычное')
                )
            return format_html(''.join(photo_html))
        return 'Нет фото'
    get_user_photos.short_description = 'Фотографии'
    
    def export_to_excel(self, request, queryset):
        """Экспорт выбранных пользователей в Excel"""
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xls"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Пользователи')
        
        # Заголовки
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        
        columns = ['ID', 'Телефон', 'Имя', 'Фамилия', 'Email', 'Доп. телефон', 'WhatsApp', 'Агентство', 'Активен', 'Супер-админ', 'Дата регистрации', 'Последний вход']
        
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
            
        # Данные
        font_style = xlwt.XFStyle()
        for obj in queryset:
            row_num += 1
            row = [
                obj.id,
                obj.phone,
                obj.first_name,
                obj.last_name,
                obj.email or '',
                obj.additional_phone or '',
                obj.whatsapp_phone or '',
                obj.agency.name,
                'Да' if obj.is_active else 'Нет',
                'Да' if obj.is_superuser else 'Нет',
                obj.created_at.strftime('%d.%m.%Y %H:%M') if obj.created_at else '',
                obj.last_login.strftime('%d.%m.%Y %H:%M') if obj.last_login else 'Никогда'
            ]
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        
        wb.save(response)
        return response
    
    export_to_excel.short_description = "📊 Экспорт в Excel"
    
    def export_all_users_to_excel(self, request, queryset):
        """Экспорт ВСЕХ пользователей в Excel"""
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="all_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xls"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Все пользователи')
        
        # Заголовки
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        
        columns = [
            'ID', 'Телефон', 'Имя', 'Фамилия', 'Email', 'Доп. телефон', 'WhatsApp', 
            'Агентство', 'Активен', 'Супер-админ', 'Персонал', 'Дата регистрации', 
            'Последний вход', 'Первый вход', 'Количество объявлений', 'Количество коллекций',
            'Количество фотографий', 'Активность (всего действий)'
        ]
        
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
            
        # Получаем ВСЕ пользователей, не только выбранные
        all_users = User.objects.all().select_related('agency').prefetch_related(
            'announcements', 'collections', 'photos', 'activities'
        )
        
        # Данные
        font_style = xlwt.XFStyle()
        for user in all_users:
            row_num += 1
            row = [
                user.id,
                user.phone,
                user.first_name,
                user.last_name,
                user.email or '',
                user.additional_phone or '',
                user.whatsapp_phone or '',
                user.agency.name if user.agency else '',
                'Да' if user.is_active else 'Нет',
                'Да' if user.is_superuser else 'Нет',
                'Да' if user.is_staff else 'Нет',
                user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else '',
                user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else 'Никогда',
                'Нет' if user.is_first_login else 'Да',
                user.announcements.count(),
                user.collections.count(),
                user.photos.count(),
                user.activities.count() if hasattr(user, 'activities') else 0
            ]
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        
        wb.save(response)
        
        # Сообщение об успешном экспорте
        self.message_user(
            request, 
            f'Экспортировано {all_users.count()} пользователей в Excel файл.', 
            messages.SUCCESS
        )
        
        return response
    
    export_all_users_to_excel.short_description = "📈 Экспорт ВСЕХ пользователей в Excel"
    
    def export_all_users_to_csv(self, request, queryset):
        """Экспорт ВСЕХ пользователей в CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="all_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response.write('\ufeff')  # BOM для корректного отображения в Excel
        
        writer = csv.writer(response)
        
        # Заголовки
        writer.writerow([
            'ID', 'Телефон', 'Имя', 'Фамилия', 'Email', 'Доп. телефон', 'WhatsApp', 
            'Агентство', 'Активен', 'Супер-админ', 'Персонал', 'Дата регистрации', 
            'Последний вход', 'Первый вход', 'Количество объявлений', 'Количество коллекций',
            'Количество фотографий', 'Активность (всего действий)'
        ])
        
        # Получаем ВСЕ пользователей, не только выбранные
        all_users = User.objects.all().select_related('agency').prefetch_related(
            'announcements', 'collections', 'photos', 'activities'
        )
        
        # Данные
        for user in all_users:
            writer.writerow([
                user.id,
                user.phone,
                user.first_name,
                user.last_name,
                user.email or '',
                user.additional_phone or '',
                user.whatsapp_phone or '',
                user.agency.name if user.agency else '',
                'Да' if user.is_active else 'Нет',
                'Да' if user.is_superuser else 'Нет',
                'Да' if user.is_staff else 'Нет',
                user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else '',
                user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else 'Никогда',
                'Нет' if user.is_first_login else 'Да',
                user.announcements.count(),
                user.collections.count(),
                user.photos.count(),
                user.activities.count() if hasattr(user, 'activities') else 0
            ])
        
        # Сообщение об успешном экспорте
        self.message_user(
            request, 
            f'Экспортировано {all_users.count()} пользователей в CSV файл.', 
            messages.SUCCESS
        )
        
        return response
    
    export_all_users_to_csv.short_description = "📋 Экспорт ВСЕХ пользователей в CSV"
    
    def delete_users_with_data(self, request, queryset):
        """Удаление пользователей со всеми связанными данными"""
        total_deleted = 0
        for user in queryset:
            # Удаляем объявления пользователя
            announcements = user.announcements.all()
            for announcement in announcements:
                # Удаляем фотографии объявления
                for photo in announcement.photos.all():
                    photo.delete()
                announcement.delete()
            
            # Удаляем коллекции пользователя
            user.collections.all().delete()
            
            # Удаляем фотографии пользователя
            for photo in user.photos.all():
                photo.delete()
                
            # Удаляем пользователя
            user.delete()
            total_deleted += 1
        
        self.message_user(request, f'Успешно удалено {total_deleted} пользователей со всеми связанными данными.', messages.SUCCESS)
    
    delete_users_with_data.short_description = "🗑️ Удалить со всеми данными"
    
    def make_superuser(self, request, queryset):
        """Сделать выбранных пользователей супер-админами"""
        updated = queryset.update(is_superuser=True, is_staff=True)
        self.message_user(request, f'{updated} пользователей сделаны супер-администраторами.', messages.SUCCESS)
    
    make_superuser.short_description = "👑 Сделать супер-админами"
    
    def make_regular_user(self, request, queryset):
        """Сделать выбранных пользователей обычными"""
        updated = queryset.update(is_superuser=False, is_staff=False)
        self.message_user(request, f'{updated} пользователей сделаны обычными.', messages.SUCCESS)
    
    make_regular_user.short_description = "👤 Сделать обычными пользователями"

    def reset_passwords(self, request, queryset):
        for user in queryset:
            user.set_password('11223344')
            user.save()
        self.message_user(request, f"Пароль выбранных пользователей сброшен на 11223344.")
    reset_passwords.short_description = "Сбросить пароль на 11223344"

    def password_reset_status(self, obj):
        from django.contrib.auth.hashers import check_password
        if check_password('11223344', obj.password):
            return 'по умолчанию'
        return ''
    password_reset_status.short_description = 'Пароль'


@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_name', 'is_main', 'uploaded_at']
    list_filter = ['is_main', 'uploaded_at']
    search_fields = ['user__first_name', 'user__last_name', 'file_name']


# ===== ОБЪЯВЛЕНИЯ =====

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_address', 'microdistrict', 'complex_name']
    search_fields = ['microdistrict', 'complex_name', 'street', 'building_no']
    list_filter = ['microdistrict']
    
    def full_address(self, obj):
        parts = []
        if obj.microdistrict:
            parts.append(obj.microdistrict)
        if obj.complex_name:
            parts.append(obj.complex_name)
        if obj.street:
            parts.append(obj.street)
        if obj.building_no:
            parts.append(f"д. {obj.building_no}")
        return ", ".join(parts)
    full_address.short_description = 'Полный адрес'


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ['file_name', 'is_main', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price_formatted', 'user', 'repair_status', 'is_archived', 'created_at']
    list_filter = ['rooms_count', 'repair_status', 'is_new_building', 'is_archived', 'created_at', 'user__agency']
    search_fields = ['user__first_name', 'user__last_name', 'description', 'address__microdistrict', 'address__complex_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['archive_announcements', 'unarchive_announcements']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'rooms_count', 'price', 'area', 'repair_status')
        }),
        ('Информация о доме', {
            'fields': ('building_type', 'year_built', 'is_new_building', 'floor', 'total_floors')
        }),
        ('Адрес', {
            'fields': ('address',)
        }),
        ('Описание', {
            'fields': ('description',)
        }),
        ('Комиссия', {
            'fields': ('commission_type', 'commission_percentage', 'commission_amount', 'commission_bonus'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('landmarks', 'krisha_link'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_archived',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PhotoInline]
    
    def title(self, obj):
        return f"{obj.rooms_count}-комнатная квартира"
    title.short_description = 'Название'
    
    def price_formatted(self, obj):
        return f"{obj.price:,} ₸".replace(',', ' ')
    price_formatted.short_description = 'Цена'
    
    def archive_announcements(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} объявлений архивировано.', messages.SUCCESS)
    
    archive_announcements.short_description = "📦 Архивировать"
    
    def unarchive_announcements(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(request, f'{updated} объявлений восстановлено из архива.', messages.SUCCESS)
    
    unarchive_announcements.short_description = "📤 Восстановить из архива"


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'file_name', 'is_main', 'uploaded_at']
    list_filter = ['is_main', 'uploaded_at']
    search_fields = ['announcement__user__first_name', 'file_name']


# ===== КОЛЛЕКЦИИ =====

class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    extra = 0
    fields = ['announcement', 'added_at']
    readonly_fields = ['added_at']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'items_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CollectionItemInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Количество объявлений'


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ['collection', 'announcement', 'added_at']
    list_filter = ['added_at']
    search_fields = ['collection__name', 'announcement__user__first_name']


# ===== ПОДПИСКИ =====

class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'tariff', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['user__first_name', 'user__last_name', 'tariff__name']
    ordering = ['-start_date']


# ===== АНАЛИТИКА =====

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time', 'duration_formatted', 'session_key']
    list_filter = ['login_time', 'logout_time']
    search_fields = ['user__first_name', 'user__last_name', 'session_key']
    ordering = ['-login_time']
    readonly_fields = ['duration']
    actions = ['export_sessions_to_csv']
    
    def duration_formatted(self, obj):
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}ч {minutes}м"
        return "Активна"
    duration_formatted.short_description = 'Длительность'
    
    def export_sessions_to_csv(self, request, queryset):
        """Экспорт сессий в CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="user_sessions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID пользователя', 'ФИО', 'Телефон', 'Время входа', 'Время выхода', 'Длительность (минуты)', 'Ключ сессии'])
        
        for session in queryset:
            duration_minutes = ""
            if session.duration:
                duration_minutes = int(session.duration.total_seconds() // 60)
            
            writer.writerow([
                session.user.id,
                f"{session.user.first_name} {session.user.last_name}",
                session.user.phone,
                session.login_time.strftime('%d.%m.%Y %H:%M:%S') if session.login_time else '',
                session.logout_time.strftime('%d.%m.%Y %H:%M:%S') if session.logout_time else 'Активна',
                duration_minutes,
                session.session_key
            ])
        
        return response
    
    export_sessions_to_csv.short_description = "📊 Экспорт в CSV"


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'path', 'timestamp', 'duration_seconds']
    list_filter = ['timestamp']
    search_fields = ['user__first_name', 'user__last_name', 'path']
    ordering = ['-timestamp']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Админка для детального отслеживания активности пользователей"""
    
    list_display = [
        'user', 'action_type', 'description', 'timestamp', 
        'is_successful', 'ip_address', 'get_page_type'
    ]
    
    list_filter = [
        'action_type', 'is_successful', 'timestamp',
        ('user', admin.RelatedOnlyFieldListFilter),
        ('related_announcement', admin.RelatedOnlyFieldListFilter),
        ('related_collection', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'user__phone', 'user__first_name', 'user__last_name',
        'description', 'ip_address', 'user_agent'
    ]
    
    readonly_fields = [
        'user', 'action_type', 'description', 'metadata',
        'ip_address', 'user_agent', 'related_announcement',
        'related_collection', 'timestamp', 'session_key',
        'page_url', 'referrer', 'is_successful', 'error_message',
        'get_formatted_metadata', 'get_user_info'
    ]
    
    fields = [
        'user', 'get_user_info', 'action_type', 'description',
        'timestamp', 'is_successful', 'error_message',
        'related_announcement', 'related_collection',
        'ip_address', 'user_agent', 'session_key',
        'page_url', 'referrer', 'get_formatted_metadata'
    ]
    
    date_hierarchy = 'timestamp'
    
    ordering = ['-timestamp']
    
    list_per_page = 50
    
    def get_page_type(self, obj):
        """Получает тип страницы из метаданных"""
        if obj.metadata and 'page_type' in obj.metadata:
            return obj.metadata['page_type']
        return '-'
    get_page_type.short_description = 'Тип страницы'
    
    def get_user_info(self, obj):
        """Получает расширенную информацию о пользователе"""
        if obj.user:
            return format_html(
                '<strong>Телефон:</strong> {}<br>'
                '<strong>Имя:</strong> {}<br>'
                '<strong>Агентство:</strong> {}<br>'
                '<strong>Дата регистрации:</strong> {}',
                obj.user.phone,
                obj.user.get_full_name() or 'Не указано',
                obj.user.agency.name if obj.user.agency else 'Не указано',
                obj.user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            )
        return '-'
    get_user_info.short_description = 'Информация о пользователе'
    
    def get_formatted_metadata(self, obj):
        """Форматированные метаданные"""
        return format_html('<pre>{}</pre>', obj.get_formatted_metadata())
    get_formatted_metadata.short_description = 'Метаданные'
    
    def has_add_permission(self, request):
        """Запрещаем добавление записей вручную"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем изменение записей"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление только суперпользователям"""
        return request.user.is_superuser
    
    # Действия для экспорта
    def export_to_csv(self, request, queryset):
        """Экспорт активности в CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="user_activity.csv"'
        response.write('\ufeff')  # BOM для корректного отображения в Excel
        
        writer = csv.writer(response)
        
        # Заголовки
        writer.writerow([
            'Пользователь', 'Телефон', 'Тип действия', 'Описание',
            'Время', 'Успешно', 'IP адрес', 'Браузер',
            'Связанное объявление', 'Связанная коллекция',
            'URL страницы', 'Referrer', 'Метаданные'
        ])
        
        # Данные
        for activity in queryset:
            writer.writerow([
                activity.user.get_full_name() or activity.user.phone,
                activity.user.phone,
                activity.get_action_type_display(),
                activity.description or '',
                activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Да' if activity.is_successful else 'Нет',
                activity.ip_address or '',
                activity.user_agent or '',
                str(activity.related_announcement) if activity.related_announcement else '',
                str(activity.related_collection) if activity.related_collection else '',
                activity.page_url or '',
                activity.referrer or '',
                activity.get_formatted_metadata()
            ])
        
        return response
    
    export_to_csv.short_description = "Экспорт выбранных записей в CSV"
    
    def export_user_activity_summary(self, request, queryset):
        """Экспорт сводки активности пользователей"""
        import csv
        from django.http import HttpResponse
        from django.db.models import Count
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="user_activity_summary.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Заголовки
        writer.writerow([
            'Пользователь', 'Телефон', 'Всего действий', 'Успешных действий',
            'Неуспешных действий', 'Последнее действие', 'Типы действий'
        ])
        
        # Группируем по пользователям
        user_stats = {}
        for activity in queryset:
            user = activity.user
            if user not in user_stats:
                user_stats[user] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'last_activity': activity.timestamp,
                    'action_types': set()
                }
            
            user_stats[user]['total'] += 1
            if activity.is_successful:
                user_stats[user]['successful'] += 1
            else:
                user_stats[user]['failed'] += 1
            
            user_stats[user]['action_types'].add(activity.get_action_type_display())
            
            if activity.timestamp > user_stats[user]['last_activity']:
                user_stats[user]['last_activity'] = activity.timestamp
        
        # Записываем данные
        for user, stats in user_stats.items():
            writer.writerow([
                user.get_full_name() or user.phone,
                user.phone,
                stats['total'],
                stats['successful'],
                stats['failed'],
                stats['last_activity'].strftime('%Y-%m-%d %H:%M:%S'),
                ', '.join(stats['action_types'])
            ])
        
        return response
    
    export_user_activity_summary.short_description = "Экспорт сводки активности пользователей"
    
    actions = ['export_to_csv', 'export_user_activity_summary']
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'user', 'user__agency', 'related_announcement', 'related_collection'
        )


# Настройка админ панели
admin.site.site_header = "ProAgentAstana - Панель администратора"
admin.site.site_title = "ProAgentAstana Admin"
admin.site.index_title = "Добро пожаловать в панель администратора"

# Убираем ненужные модели из админки
admin.site.unregister(Group)


from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserActivity, UserSession
from django.db import transaction, connection
from django.http import HttpResponseRedirect
import json
import logging
import psycopg2

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires users to be authenticated to access any page
    except login, register, and admin pages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process the request and check if user is authenticated
        """
        # Пропускаем проверку для статических файлов, медиа и админки
        if (request.path.startswith('/static/') or 
            request.path.startswith('/media/') or 
            request.path.startswith('/admin/')):
            return None
        
        # Проверяем, если пользователь уже аутентифицирован
        if request.user.is_authenticated:
            # Проверяем агентство "Прочее" и показываем уведомление
            self._check_agency_notification(request)
            return None
        
        # Страницы, которые доступны без авторизации
        public_paths = ['/login/', '/register/']
        
        # AJAX эндпоинты, доступные без авторизации
        ajax_public_paths = ['/ajax/agency-autocomplete/']
        
        # Проверяем, если это публичная страница
        if request.path in public_paths:
            return None
        
        # Проверяем, если это публичный AJAX эндпоинт
        if request.path in ajax_public_paths:
            return None
        
        # Если пользователь не аутентифицирован и пытается зайти на защищенную страницу
        messages.info(request, 'Пожалуйста, войдите в систему или зарегистрируйтесь для доступа к сайту.')
        return redirect('login')
    
    def _check_agency_notification(self, request):
        """
        Проверяем, нужно ли показать уведомление об изменении агентства
        """
        # Проверяем только для аутентифицированных пользователей
        if not request.user.is_authenticated:
            return
            
        # Проверяем, если агентство пользователя "Прочее"
        if hasattr(request.user, 'agency') and request.user.agency and request.user.agency.name == 'Прочее':
            # Проверяем, что мы не на странице смены агентства, чтобы не показывать уведомление постоянно
            if request.path not in ['/account/', '/logout/']:
                # Проверяем, что уведомление еще не показывалось в этой сессии
                if not request.session.get('agency_notification_shown', False):
                    messages.warning(
                        request,
                        'Ваше агентство было удалено и установлено как "Прочее". '
                        'Пожалуйста, обновите информацию о вашем агентстве в '
                        '<a href="/account/" class="alert-link">личном кабинете</a>.'
                    )
                    # Отмечаем, что уведомление показано в этой сессии
                    request.session['agency_notification_shown'] = True
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process view and handle specific cases
        """
        return None 


class UserActivityMiddleware(MiddlewareMixin):
    """Middleware для автоматического логирования активности пользователей"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Обработка входящих запросов"""
        # Сохраняем время начала запроса
        request._activity_start_time = timezone.now()
        
        # Получаем информацию о пользователе
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Логируем просмотр страницы только для GET запросов
            if request.method == 'GET':
                try:
                    self.log_page_view(request)
                except Exception as e:
                    logger.error(f"Ошибка при логировании просмотра страницы: {e}")
        
        return None
    
    def process_response(self, request, response):
        """Обработка исходящих ответов"""
        # Можно добавить логику для обработки ответов
        return response
    
    def log_page_view(self, request):
        """Логирование просмотра страницы"""
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        # Исключаем системные URL
        excluded_paths = [
            '/admin/jsi18n/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/ajax/',
            '/api/',
        ]
        
        # Проверяем, не является ли путь исключенным
        for excluded_path in excluded_paths:
            if request.path.startswith(excluded_path):
                return
        
        # Получаем дополнительную информацию
        metadata = {}
        
        # Добавляем GET параметры если они есть
        if request.GET:
            metadata['get_params'] = dict(request.GET)
        
        # Добавляем информацию о том, что это за страница
        page_type = self.get_page_type(request.path)
        if page_type:
            metadata['page_type'] = page_type
        
        # Создаем запись об активности
        try:
            with transaction.atomic():
                UserActivity.objects.create(
                    user=request.user,
                    action_type='view_page',
                    description=f"Просмотр страницы {request.path}",
                    metadata=metadata if metadata else None,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    session_key=request.session.session_key,
                    page_url=request.build_absolute_uri(),
                    referrer=request.META.get('HTTP_REFERER', ''),
                    is_successful=True
                )
        except Exception as e:
            logger.error(f"Ошибка при создании записи об активности: {e}")
    
    def get_page_type(self, path):
        """Определяет тип страницы по URL"""
        if path == '/':
            return 'main_page'
        elif path.startswith('/announcements/'):
            if '/create/' in path:
                return 'create_announcement'
            elif '/edit/' in path:
                return 'edit_announcement'
            elif path.count('/') == 2:  # /announcements/123/
                return 'announcement_detail'
            else:
                return 'announcements_list'
        elif path.startswith('/collections/'):
            if '/create/' in path:
                return 'create_collection'
            elif '/edit/' in path:
                return 'edit_collection'
            elif path.count('/') == 2:  # /collections/123/
                return 'collection_detail'
            else:
                return 'collections_list'
        elif path.startswith('/profile/'):
            return 'profile'
        elif path.startswith('/search/'):
            return 'search'
        elif path.startswith('/login/'):
            return 'login'
        elif path.startswith('/register/'):
            return 'register'
        elif path.startswith('/logout/'):
            return 'logout'
        
        return None
    
    def get_client_ip(self, request):
        """Получает IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserSessionMiddleware(MiddlewareMixin):
    """Middleware для отслеживания сессий пользователей"""
    
    def process_request(self, request):
        """Обработка входящих запросов для отслеживания сессий"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            session_key = request.session.session_key
            
            if session_key:
                try:
                    # Получаем или создаем сессию
                    session, created = UserSession.objects.get_or_create(
                        user=request.user,
                        session_key=session_key,
                        defaults={
                            'login_time': timezone.now(),
                        }
                    )
                    
                    # Если сессия уже существует, обновляем время последней активности
                    if not created:
                        # Можно добавить поле last_activity в модель UserSession
                        pass
                        
                except Exception as e:
                    logger.error(f"Ошибка при обработке сессии: {e}")
        
        return None


class DatabaseErrorMiddleware(MiddlewareMixin):
    """
    Middleware для обработки ошибок курсора базы данных Neon
    """
    
    def process_exception(self, request, exception):
        """Обрабатывает исключения базы данных"""
        
        # Проверяем на ошибки курсора
        if isinstance(exception, (psycopg2.InterfaceError, psycopg2.OperationalError)):
            error_message = str(exception).lower()
            
            # Обрабатываем ошибки курсора
            if 'cursor' in error_message and ('does not exist' in error_message or 'closed' in error_message):
                logger.warning(f"Database cursor error: {exception}")
                
                # Закрываем соединение для переподключения
                try:
                    connection.close()
                except:
                    pass
                
                # Перенаправляем на ту же страницу для повторной попытки
                messages.error(request, 'Временная проблема с подключением к базе данных. Пожалуйста, попробуйте снова.')
                return HttpResponseRedirect(request.get_full_path())
            
            # Другие ошибки БД
            elif 'connection' in error_message:
                logger.error(f"Database connection error: {exception}")
                messages.error(request, 'Проблема с подключением к базе данных. Обновите страницу.')
                return HttpResponseRedirect(request.get_full_path())
        
        # Возвращаем None для других исключений
        return None 
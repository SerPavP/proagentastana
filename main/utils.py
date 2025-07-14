from django.core.files.storage import default_storage
from django.conf import settings
from .models import Photo, UserPhoto
import os
from PIL import Image
import io
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import UserActivity
import logging


User = get_user_model()
logger = logging.getLogger(__name__)


def get_photo_stats():
    """
    Get statistics about photo optimization
    """
    stats = {
        'announcement_photos': {
            'count': 0,
            'total_size': 0,
            'optimized_count': 0,
            'thumbnails_count': 0,
            'average_size': 0
        },
        'user_photos': {
            'count': 0,
            'total_size': 0,
            'optimized_count': 0,
            'average_size': 0
        }
    }
    
    # Announcement photos stats
    announcement_photos = Photo.objects.all()
    for photo in announcement_photos:
        stats['announcement_photos']['count'] += 1
        stats['announcement_photos']['total_size'] += photo.file_size or 0
        
        if photo.thumbnail_path:
            stats['announcement_photos']['thumbnails_count'] += 1
            
        if photo.mime_type == 'image/jpeg':
            stats['announcement_photos']['optimized_count'] += 1
    
    if stats['announcement_photos']['count'] > 0:
        stats['announcement_photos']['average_size'] = (
            stats['announcement_photos']['total_size'] / stats['announcement_photos']['count']
        )
    
    # User photos stats
    user_photos = UserPhoto.objects.all()
    for photo in user_photos:
        stats['user_photos']['count'] += 1
        stats['user_photos']['total_size'] += photo.file_size or 0
        
        if photo.mime_type == 'image/jpeg':
            stats['user_photos']['optimized_count'] += 1
    
    if stats['user_photos']['count'] > 0:
        stats['user_photos']['average_size'] = (
            stats['user_photos']['total_size'] / stats['user_photos']['count']
        )
    
    return stats


def format_file_size(size_bytes):
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"


def estimate_storage_savings():
    """
    Estimate storage savings from optimization
    """
    stats = get_photo_stats()
    
    # Estimate unoptimized size (assuming 3MB average for announcement photos, 1MB for user photos)
    estimated_unoptimized_announcement = stats['announcement_photos']['count'] * 3 * 1024 * 1024  # 3MB each
    estimated_unoptimized_user = stats['user_photos']['count'] * 1 * 1024 * 1024  # 1MB each
    
    actual_total = stats['announcement_photos']['total_size'] + stats['user_photos']['total_size']
    estimated_total = estimated_unoptimized_announcement + estimated_unoptimized_user
    
    savings = estimated_total - actual_total
    savings_percent = (savings / estimated_total * 100) if estimated_total > 0 else 0
    
    return {
        'estimated_unoptimized_size': estimated_total,
        'actual_size': actual_total,
        'savings_bytes': savings,
        'savings_percent': savings_percent,
        'formatted_estimated': format_file_size(estimated_total),
        'formatted_actual': format_file_size(actual_total),
        'formatted_savings': format_file_size(savings)
    }


def validate_image_file(file):
    """
    Validate uploaded image file
    """
    errors = []
    
    # Check file size
    max_size = getattr(settings, 'IMAGE_OPTIMIZATION', {}).get('MAX_FILE_SIZE', 10 * 1024 * 1024)
    if file.size > max_size:
        errors.append(f"File size too large. Maximum size is {format_file_size(max_size)}")
    
    # Check if it's an image
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        errors.append("Invalid image file")
        return errors
    
    # Reset file pointer after verification
    file.seek(0)
    
    # Check image format
    allowed_formats = ['JPEG', 'PNG', 'WEBP', 'GIF', 'BMP']
    if img.format not in allowed_formats:
        errors.append(f"Unsupported image format: {img.format}. Allowed formats: {', '.join(allowed_formats)}")
    
    return errors


def get_image_info(file):
    """
    Get information about an image file
    """
    try:
        img = Image.open(file)
        info = {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'file_size': file.size,
            'formatted_size': format_file_size(file.size)
        }
        
        # Estimate optimized size (rough calculation)
        estimated_optimized_size = file.size * 0.3  # Assume 70% compression
        info['estimated_optimized_size'] = estimated_optimized_size
        info['formatted_estimated_optimized'] = format_file_size(estimated_optimized_size)
        
        return info
    except Exception as e:
        return {'error': str(e)} 


def log_user_activity(user, action_type, description=None, metadata=None, 
                      request=None, related_announcement=None, 
                      related_collection=None, is_successful=True, 
                      error_message=None):
    """
    Утилита для логирования активности пользователей
    
    Args:
        user: Пользователь
        action_type: Тип действия (из UserActivity.ACTION_TYPES)
        description: Описание действия
        metadata: Дополнительные данные в виде словаря
        request: HTTP запрос (для получения IP, User-Agent и т.д.)
        related_announcement: Связанное объявление
        related_collection: Связанная коллекция
        is_successful: Успешность выполнения действия
        error_message: Сообщение об ошибке (если есть)
    """
    try:
        with transaction.atomic():
            activity_data = {
                'user': user,
                'action_type': action_type,
                'description': description,
                'metadata': metadata,
                'related_announcement': related_announcement,
                'related_collection': related_collection,
                'is_successful': is_successful,
                'error_message': error_message,
                'timestamp': timezone.now()
            }
            
            # Добавляем данные из запроса если он предоставлен
            if request:
                activity_data.update({
                    'ip_address': get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'session_key': request.session.session_key if hasattr(request, 'session') else None,
                    'page_url': request.build_absolute_uri() if hasattr(request, 'build_absolute_uri') else None,
                    'referrer': request.META.get('HTTP_REFERER', ''),
                })
            
            UserActivity.objects.create(**activity_data)
            
    except Exception as e:
        logger.error(f"Ошибка при логировании активности пользователя: {e}")


def get_client_ip(request):
    """Получает IP адрес клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Декоратор для автоматического логирования действий в views
def log_activity(action_type, description=None, get_related_announcement=None, 
                 get_related_collection=None):
    """
    Декоратор для автоматического логирования действий в views
    
    Args:
        action_type: Тип действия
        description: Описание действия (может быть функцией)
        get_related_announcement: Функция для получения связанного объявления
        get_related_collection: Функция для получения связанной коллекции
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                # Выполняем оригинальную функцию
                result = view_func(request, *args, **kwargs)
                
                # Логируем успешное выполнение
                if request.user.is_authenticated:
                    desc = description
                    if callable(description):
                        desc = description(request, *args, **kwargs)
                    
                    related_announcement = None
                    if get_related_announcement:
                        related_announcement = get_related_announcement(request, *args, **kwargs)
                    
                    related_collection = None
                    if get_related_collection:
                        related_collection = get_related_collection(request, *args, **kwargs)
                    
                    log_user_activity(
                        user=request.user,
                        action_type=action_type,
                        description=desc,
                        request=request,
                        related_announcement=related_announcement,
                        related_collection=related_collection,
                        is_successful=True
                    )
                
                return result
                
            except Exception as e:
                # Логируем ошибку
                if request.user.is_authenticated:
                    log_user_activity(
                        user=request.user,
                        action_type='error',
                        description=f"Ошибка при выполнении {action_type}",
                        request=request,
                        is_successful=False,
                        error_message=str(e)
                    )
                raise
        
        return wrapper
    return decorator


# Специальные функции для логирования конкретных действий
def log_login(user, request):
    """Логирование входа в систему"""
    log_user_activity(
        user=user,
        action_type='login',
        description=f"Пользователь {user.get_full_name() or user.phone} вошел в систему",
        request=request,
        metadata={
            'login_time': timezone.now().isoformat(),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': get_client_ip(request)
        }
    )


def log_logout(user, request):
    """Логирование выхода из системы"""
    log_user_activity(
        user=user,
        action_type='logout',
        description=f"Пользователь {user.get_full_name() or user.phone} вышел из системы",
        request=request,
        metadata={
            'logout_time': timezone.now().isoformat()
        }
    )


def log_announcement_action(user, action_type, announcement, request=None, old_values=None, new_values=None):
    """Логирование действий с объявлениями"""
    metadata = {}
    if old_values:
        metadata['old_values'] = old_values
    if new_values:
        metadata['new_values'] = new_values
    
    descriptions = {
        'create_announcement': f"Создано объявление '{announcement.id}' - {announcement.rooms_count} комн., {announcement.price} тенге",
        'edit_announcement': f"Отредактировано объявление '{announcement.id}'",
        'delete_announcement': f"Удалено объявление '{announcement.id}'",
        'archive_announcement': f"Архивировано объявление '{announcement.id}'",
        'unarchive_announcement': f"Восстановлено объявление '{announcement.id}'",
        'view_announcement': f"Просмотрено объявление '{announcement.id}'"
    }
    
    log_user_activity(
        user=user,
        action_type=action_type,
        description=descriptions.get(action_type, f"Действие с объявлением '{announcement.id}'"),
        request=request,
        related_announcement=announcement,
        metadata=metadata if metadata else None
    )


def log_collection_action(user, action_type, collection, request=None, announcement=None):
    """Логирование действий с коллекциями"""
    descriptions = {
        'create_collection': f"Создана коллекция '{collection.name}'",
        'edit_collection': f"Отредактирована коллекция '{collection.name}'",
        'delete_collection': f"Удалена коллекция '{collection.name}'",
        'add_to_collection': f"Добавлено объявление в коллекцию '{collection.name}'",
        'remove_from_collection': f"Удалено объявление из коллекции '{collection.name}'",
        'view_collection': f"Просмотрена коллекция '{collection.name}'"
    }
    
    metadata = {}
    if announcement:
        metadata['announcement_id'] = announcement.id
    
    log_user_activity(
        user=user,
        action_type=action_type,
        description=descriptions.get(action_type, f"Действие с коллекцией '{collection.name}'"),
        request=request,
        related_collection=collection,
        related_announcement=announcement,
        metadata=metadata if metadata else None
    )


def log_search_action(user, search_params, request=None):
    """Логирование поиска"""
    log_user_activity(
        user=user,
        action_type='search_announcements',
        description=f"Выполнен поиск объявлений",
        request=request,
        metadata={
            'search_params': search_params,
            'search_time': timezone.now().isoformat()
        }
    )


def log_filter_action(user, filter_params, request=None):
    """Логирование фильтрации"""
    log_user_activity(
        user=user,
        action_type='filter_announcements',
        description=f"Применены фильтры к объявлениям",
        request=request,
        metadata={
            'filter_params': filter_params,
            'filter_time': timezone.now().isoformat()
        }
    ) 
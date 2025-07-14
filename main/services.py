from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import (
    Agency, User, UserPhoto, Address, Announcement, Photo, 
    Collection, CollectionItem, UserSession, PageView
)
import os
import uuid
from datetime import timedelta
from PIL import Image, ImageOps
import io


class AgencyService:
    """Service class for working with agencies"""
    
    @staticmethod
    def create_agency(name):
        """Create a new agency"""
        return Agency.objects.create(name=name)
    
    @staticmethod
    def get_agency_by_id(agency_id):
        """Get agency by ID"""
        try:
            return Agency.objects.get(id=agency_id)
        except Agency.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_agencies():
        """Get all agencies"""
        return Agency.objects.all()


class UserService:
    """Service class for working with users"""
    
    @staticmethod
    def create_user(first_name, last_name, phone, password, agency, **kwargs):
        """Create a new user"""
        # Используем метод create_user менеджера для правильной обработки пароля
        user = User.objects.create_user(
            phone=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
            agency=agency,
            email=kwargs.get('email', ''),
            additional_phone=kwargs.get('additional_phone', ''),
            whatsapp_phone=kwargs.get('whatsapp_phone', ''),
        )
        return user
    
    @staticmethod
    def get_user_by_phone(phone):
        """Get user by phone number"""
        try:
            return User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def update_user(user, **kwargs):
        """Update user information"""
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()
        return user
    
    @staticmethod
    def deactivate_user(user):
        """Deactivate user"""
        user.is_active = False
        user.save()
        return user


class AddressService:
    """Service class for working with addresses"""
    
    @staticmethod
    def create_address(**kwargs):
        """Create a new address"""
        return Address.objects.create(**kwargs)
    
    @staticmethod
    def get_address_by_id(address_id):
        """Get address by ID"""
        try:
            return Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return None
    
    @staticmethod
    def update_address(address, **kwargs):
        """Update address information"""
        for field, value in kwargs.items():
            if hasattr(address, field):
                setattr(address, field, value)
        address.save()
        return address


class AnnouncementService:
    """Service class for working with announcements"""
    
    @staticmethod
    def create_announcement(user, address_data, **announcement_data):
        """Create a new announcement with address"""
        with transaction.atomic():
            address = AddressService.create_address(**address_data)
            announcement_data['address'] = address
            announcement_data['user'] = user
            return Announcement.objects.create(**announcement_data)
    
    @staticmethod
    def get_announcement_by_id(announcement_id):
        """Get announcement by ID"""
        try:
            return Announcement.objects.select_related('user', 'address').get(id=announcement_id)
        except Announcement.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_announcements(user, include_archived=False):
        """Get all announcements for a user"""
        queryset = Announcement.objects.filter(user=user).select_related('address')
        if not include_archived:
            queryset = queryset.filter(is_archived=False)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_archived_user_announcements(user):
        """Get all archived announcements for a user"""
        return Announcement.objects.filter(user=user, is_archived=True).select_related('address').order_by('-updated_at')

    @staticmethod
    def get_all_announcements(include_archived=False):
        """Get all announcements"""
        queryset = Announcement.objects.select_related('user', 'address')
        if not include_archived:
            queryset = queryset.filter(is_archived=False)
        return queryset.order_by('-created_at')
    
    @staticmethod
    def update_announcement(announcement, **kwargs):
        """Update announcement"""
        for field, value in kwargs.items():
            if hasattr(announcement, field):
                setattr(announcement, field, value)
        announcement.save()
        return announcement
    
    @staticmethod
    def archive_announcement(announcement):
        """Archive announcement"""
        announcement.is_archived = True
        announcement.save()
        return announcement
    
    @staticmethod
    def delete_announcement(announcement):
        """Delete announcement"""
        announcement.delete()


class CollectionService:
    """Service class for working with collections"""
    
    @staticmethod
    def create_collection(user, name):
        """Create a new collection"""
        return Collection.objects.create(user=user, name=name)
    
    @staticmethod
    def get_collection_by_id(collection_id):
        """Get collection by ID"""
        try:
            return Collection.objects.select_related('user').get(id=collection_id)
        except Collection.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_collections(user):
        """Get all collections for a user"""
        return Collection.objects.filter(user=user).order_by('-created_at')
    
    @staticmethod
    def add_announcement_to_collection(collection, announcement):
        """Add announcement to collection"""
        collection_item, created = CollectionItem.objects.get_or_create(
            collection=collection,
            announcement=announcement
        )
        return collection_item, created
    
    @staticmethod
    def remove_announcement_from_collection(collection, announcement):
        """Remove announcement from collection"""
        try:
            item = CollectionItem.objects.get(collection=collection, announcement=announcement)
            item.delete()
            return True
        except CollectionItem.DoesNotExist:
            return False
    
    @staticmethod
    def get_collection_announcements(collection, include_archived=True):
        """Get all announcements in a collection"""
        queryset = Announcement.objects.filter(
            collection_items__collection=collection
        ).select_related('user', 'address').order_by('-collection_items__added_at')
        
        if not include_archived:
            queryset = queryset.filter(is_archived=False)
        
        return queryset
    
    @staticmethod
    def get_active_collection_announcements(collection):
        """Get only active (non-archived) announcements in a collection"""
        return CollectionService.get_collection_announcements(collection, include_archived=False)
    
    @staticmethod
    def get_archived_collection_announcements(collection):
        """Get only archived announcements in a collection"""
        return Announcement.objects.filter(
            collection_items__collection=collection,
            is_archived=True
        ).select_related('user', 'address').order_by('-collection_items__added_at')
    
    @staticmethod
    def delete_collection(collection):
        """Delete collection"""
        collection.delete()


class UserSessionService:
    """Service class for working with user sessions"""
    
    @staticmethod
    def create_session(user, session_key):
        """Create a new user session"""
        return UserSession.objects.create(
            user=user,
            session_key=session_key,
            login_time=timezone.now()
        )
    
    @staticmethod
    def end_session(session_key):
        """End a user session"""
        try:
            session = UserSession.objects.get(session_key=session_key, logout_time__isnull=True)
            session.logout_time = timezone.now()
            session.duration = session.logout_time - session.login_time
            session.save()
            return session
        except UserSession.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_sessions(user, limit=10):
        """Get user sessions"""
        return UserSession.objects.filter(user=user).order_by('-login_time')[:limit]


class PageViewService:
    """Service class for logging page views"""
    
    @staticmethod
    def log_page_view(user, path):
        """Log a page view"""
        return PageView.objects.create(user=user, path=path)
    
    @staticmethod
    def update_page_view_duration(page_view, duration_seconds):
        """Update page view duration"""
        page_view.duration_seconds = duration_seconds
        page_view.save()
        return page_view
    
    @staticmethod
    def get_user_page_views(user, limit=50):
        """Get user page views"""
        return PageView.objects.filter(user=user).order_by('-timestamp')[:limit]


class PhotoService:
    """Service class for handling photo uploads"""
    
    @staticmethod
    def _optimize_image(image_file, max_width=None, max_height=None, quality=None, image_type='announcement'):
        """
        Optimize image: resize and compress
        Returns optimized image bytes and new size
        """
        # Get settings
        image_settings = getattr(settings, 'IMAGE_OPTIMIZATION', {})
        
        if image_type == 'announcement':
            config = image_settings.get('ANNOUNCEMENT_PHOTOS', {})
            max_width = max_width or config.get('MAX_WIDTH', 1920)
            max_height = max_height or config.get('MAX_HEIGHT', 1080)
            quality = quality or config.get('QUALITY', 85)
        else:  # user photos
            config = image_settings.get('USER_PHOTOS', {})
            max_width = max_width or config.get('MAX_WIDTH', 800)
            max_height = max_height or config.get('MAX_HEIGHT', 800)
            quality = quality or config.get('QUALITY', 90)
        
        # Open image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Auto-orient image based on EXIF data
        img = ImageOps.exif_transpose(img)
        
        # Resize if too large
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save optimized image to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=quality, optimize=True)
        img_bytes.seek(0)
        
        return img_bytes, img_bytes.tell()
    
    @staticmethod
    def _create_thumbnail(image_file, size=None):
        """Create thumbnail image"""
        # Get thumbnail size from settings
        if size is None:
            image_settings = getattr(settings, 'IMAGE_OPTIMIZATION', {})
            size = image_settings.get('ANNOUNCEMENT_PHOTOS', {}).get('THUMBNAIL_SIZE', (400, 300))
        
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Auto-orient image
        img = ImageOps.exif_transpose(img)
        
        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save thumbnail to bytes
        thumb_bytes = io.BytesIO()
        img.save(thumb_bytes, format='JPEG', quality=80, optimize=True)
        thumb_bytes.seek(0)
        
        return thumb_bytes, thumb_bytes.tell()
    
    @staticmethod
    def save_announcement_photo(announcement, photo_file):
        """Save optimized announcement photo with thumbnail"""
        # Generate unique filename
        original_name = photo_file.name
        unique_id = str(uuid.uuid4())
        
        # Reset file pointer for multiple reads
        photo_file.seek(0)
        
        # Optimize main image
        optimized_img, optimized_size = PhotoService._optimize_image(photo_file, image_type='announcement')
        filename = f"{unique_id}.jpg"
        
        # Save optimized image
        file_path = f"announcement_photos/{filename}"
        saved_path = default_storage.save(file_path, ContentFile(optimized_img.read()))
        
        # Reset file pointer for thumbnail creation
        photo_file.seek(0)
        
        # Create thumbnail
        thumbnail_img, thumbnail_size = PhotoService._create_thumbnail(photo_file)
        thumbnail_filename = f"{unique_id}_thumb.jpg"
        thumbnail_path = f"announcement_photos/thumbnails/{thumbnail_filename}"
        saved_thumbnail_path = default_storage.save(thumbnail_path, ContentFile(thumbnail_img.read()))
        
        # Create photo record
        photo = Photo.objects.create(
            announcement=announcement,
            file_name=filename,
            file_path=saved_path,
            file_size=optimized_size,
            mime_type='image/jpeg',
            original_name=original_name,
            thumbnail_path=saved_thumbnail_path,
            thumbnail_size=thumbnail_size
        )
        
        return photo
    
    @staticmethod
    def save_user_photo(user, photo_file):
        """Save optimized user photo"""
        # Generate unique filename
        original_name = photo_file.name
        unique_id = str(uuid.uuid4())
        
        # Optimize user photo (smaller size for profile pics)
        optimized_img, optimized_size = PhotoService._optimize_image(
            photo_file, 
            image_type='user'
        )
        filename = f"{unique_id}.jpg"
        
        # Save optimized image
        file_path = f"user_photos/{filename}"
        saved_path = default_storage.save(file_path, ContentFile(optimized_img.read()))
        
        # Create photo record
        photo = UserPhoto.objects.create(
            user=user,
            file_name=filename,
            file_path=saved_path,
            file_size=optimized_size,
            mime_type='image/jpeg',
            original_name=original_name
        )
        
        return photo
    
    @staticmethod
    def set_main_photo(photo, is_announcement=True):
        """Set photo as main photo"""
        if is_announcement:
            # Remove main flag from other photos of the same announcement
            Photo.objects.filter(announcement=photo.announcement).update(is_main=False)
        else:
            # Remove main flag from other photos of the same user
            UserPhoto.objects.filter(user=photo.user).update(is_main=False)
        
        photo.is_main = True
        photo.save()
        return photo


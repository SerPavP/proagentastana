from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from main.models import Photo, UserPhoto
from main.services import PhotoService
import os
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Optimize existing photos and create thumbnails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes',
        )
        parser.add_argument(
            '--type',
            choices=['announcement', 'user', 'all'],
            default='all',
            help='Type of photos to optimize',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        photo_type = options['type']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        if photo_type in ['announcement', 'all']:
            self.optimize_announcement_photos(dry_run)
        
        if photo_type in ['user', 'all']:
            self.optimize_user_photos(dry_run)

    def optimize_announcement_photos(self, dry_run=False):
        """Optimize announcement photos"""
        self.stdout.write('Optimizing announcement photos...')
        
        photos = Photo.objects.filter(thumbnail_path__isnull=True)
        total = photos.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No announcement photos to optimize'))
            return
        
        self.stdout.write(f'Found {total} announcement photos to optimize')
        
        for i, photo in enumerate(photos, 1):
            self.stdout.write(f'Processing {i}/{total}: {photo.file_name}')
            
            if dry_run:
                continue
                
            try:
                # Check if file exists
                if not default_storage.exists(photo.file_path):
                    self.stdout.write(self.style.ERROR(f'File not found: {photo.file_path}'))
                    continue
                
                # Open original file
                with default_storage.open(photo.file_path, 'rb') as f:
                    file_content = f.read()
                
                # Create thumbnail
                img_bytes = io.BytesIO(file_content)
                thumbnail_img, thumbnail_size = PhotoService._create_thumbnail(img_bytes)
                
                # Generate thumbnail filename
                base_name = os.path.splitext(photo.file_name)[0]
                thumbnail_filename = f"{base_name}_thumb.jpg"
                thumbnail_path = f"announcement_photos/thumbnails/{thumbnail_filename}"
                
                # Save thumbnail
                saved_thumbnail_path = default_storage.save(
                    thumbnail_path, 
                    ContentFile(thumbnail_img.read())
                )
                
                # Update photo record
                photo.thumbnail_path = saved_thumbnail_path
                photo.thumbnail_size = thumbnail_size
                photo.save()
                
                self.stdout.write(self.style.SUCCESS(f'✓ Optimized: {photo.file_name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error processing {photo.file_name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Announcement photos optimization completed'))

    def optimize_user_photos(self, dry_run=False):
        """Optimize user photos"""
        self.stdout.write('Optimizing user photos...')
        
        photos = UserPhoto.objects.all()
        total = photos.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No user photos to optimize'))
            return
        
        self.stdout.write(f'Found {total} user photos to optimize')
        
        for i, photo in enumerate(photos, 1):
            self.stdout.write(f'Processing {i}/{total}: {photo.file_name}')
            
            if dry_run:
                continue
                
            try:
                # Check if file exists
                if not default_storage.exists(photo.file_path):
                    self.stdout.write(self.style.ERROR(f'File not found: {photo.file_path}'))
                    continue
                
                # Open original file
                with default_storage.open(photo.file_path, 'rb') as f:
                    file_content = f.read()
                
                # Re-optimize user photo if it's not JPEG or too large
                img_bytes = io.BytesIO(file_content)
                img = Image.open(img_bytes)
                
                # Check if needs optimization
                needs_optimization = (
                    img.format != 'JPEG' or 
                    img.width > 800 or 
                    img.height > 800 or
                    len(file_content) > 500000  # 500KB
                )
                
                if needs_optimization:
                    # Re-optimize
                    img_bytes.seek(0)
                    optimized_img, optimized_size = PhotoService._optimize_image(
                        img_bytes, max_width=800, max_height=800, quality=90
                    )
                    
                    # Save optimized image
                    new_filename = f"{os.path.splitext(photo.file_name)[0]}.jpg"
                    new_path = f"user_photos/{new_filename}"
                    
                    # Remove old file
                    if default_storage.exists(photo.file_path):
                        default_storage.delete(photo.file_path)
                    
                    # Save new file
                    saved_path = default_storage.save(new_path, ContentFile(optimized_img.read()))
                    
                    # Update photo record
                    photo.file_path = saved_path
                    photo.file_name = new_filename
                    photo.file_size = optimized_size
                    photo.mime_type = 'image/jpeg'
                    photo.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'✓ Optimized: {photo.file_name}'))
                else:
                    self.stdout.write(f'- Already optimized: {photo.file_name}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error processing {photo.file_name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('User photos optimization completed')) 
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import Announcement
from main.utils import log_user_activity


class Command(BaseCommand):
    help = 'Archive announcements that are older than 30 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after which to archive announcements (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be archived without actually archiving',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calculate the cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find announcements older than the cutoff date that are not already archived
        old_announcements = Announcement.objects.filter(
            created_at__lt=cutoff_date,
            is_archived=False
        )
        
        count = old_announcements.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: {count} announcements would be archived')
            )
            for announcement in old_announcements:
                self.stdout.write(
                    f'  - Announcement #{announcement.pk} created {announcement.created_at}'
                )
            return
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No announcements to archive')
            )
            return
        
        # Archive the announcements
        archived_announcements = []
        for announcement in old_announcements:
            announcement.is_archived = True
            announcement.save()
            archived_announcements.append(announcement)
            
            # Log the auto-archive action
            try:
                log_user_activity(
                    user=announcement.user,
                    action_type='auto_archive_announcement',
                    description=f'Объявление #{announcement.pk} автоматически помещено в архив (старше {days} дней)',
                    related_announcement=announcement,
                    is_successful=True
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to log activity for announcement #{announcement.pk}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully archived {count} announcements older than {days} days')
        )
        
        # Display details about archived announcements
        for announcement in archived_announcements:
            self.stdout.write(
                f'  - Archived announcement #{announcement.pk} (created {announcement.created_at})'
            ) 
from django.core.management.base import BaseCommand
from main.models import Agency, User, Address, Announcement
from main.services import UserService, AnnouncementService


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample agencies...')
        
        # Create sample agencies
        agencies_data = [
            'ProAgentAstana',
            'Astana Real Estate',
            'Capital Properties',
            'Elite Realty Astana',
            'Premier Properties'
        ]
        
        agencies = []
        for agency_name in agencies_data:
            agency, created = Agency.objects.get_or_create(name=agency_name)
            agencies.append(agency)
            if created:
                self.stdout.write(f'Created agency: {agency_name}')
        
        self.stdout.write('Sample agencies created successfully!')
        
        # Create a sample user for testing
        if not User.objects.filter(phone='+77771234567').exists():
            sample_user = UserService.create_user(
                first_name='John',
                last_name='Doe',
                phone='+77771234567',
                password='testpass123',
                agency=agencies[0],
                email='john.doe@example.com'
            )
            self.stdout.write(f'Created sample user: {sample_user.phone}')
            
            # Create sample announcements
            sample_addresses = [
                {
                    'microdistrict': 'Saryarka',
                    'complex_name': 'Highvill Astana',
                    'street': 'Turan Avenue',
                    'building_no': '37'
                },
                {
                    'microdistrict': 'Esil',
                    'complex_name': 'Emerald Towers',
                    'street': 'Kabanbay Batyr Avenue',
                    'building_no': '15'
                },
                {
                    'microdistrict': 'Almaty',
                    'street': 'Dostyk Street',
                    'building_no': '12'
                }
            ]
            
            sample_announcements = [
                {
                    'rooms_count': 2,
                    'price': 85000,
                    'repair_status': 'new',
                    'area': 65.5,
                    'floor': 5,
                    'total_floors': 12,
                    'is_new_building': True,
                    'description': 'Beautiful 2-room apartment in a new residential complex with modern amenities.'
                },
                {
                    'rooms_count': 3,
                    'price': 120000,
                    'repair_status': 'neat',
                    'area': 85.0,
                    'floor': 8,
                    'total_floors': 16,
                    'is_new_building': True,
                    'description': 'Spacious 3-room apartment with panoramic city views.'
                },
                {
                    'rooms_count': 1,
                    'price': 55000,
                    'repair_status': 'old',
                    'area': 42.0,
                    'floor': 3,
                    'total_floors': 9,
                    'is_new_building': False,
                    'description': 'Cozy 1-room apartment in established neighborhood.'
                }
            ]
            
            for i, announcement_data in enumerate(sample_announcements):
                try:
                    announcement = AnnouncementService.create_announcement(
                        user=sample_user,
                        address_data=sample_addresses[i],
                        **announcement_data
                    )
                    self.stdout.write(f'Created sample announcement: {announcement.rooms_count}-room apartment')
                except Exception as e:
                    self.stdout.write(f'Error creating announcement: {e}')
        
        self.stdout.write(
            self.style.SUCCESS('Sample data populated successfully!')
        )


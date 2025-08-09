import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import ResidentialComplex, Microdistrict


class Command(BaseCommand):
    help = 'Import housing complexes from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='housing_complexes_v2_utf8.csv',
            help='CSV file path (default: housing_complexes_v2_utf8.csv)'
        )
        parser.add_argument(
            '--microdistrict',
            type=str,
            default='default',
            help='Default microdistrict code (default: "default")'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        microdistrict_code = options['microdistrict']
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File {file_path} not found!')
            )
            return

        # Get or create default microdistrict
        microdistrict, created = Microdistrict.objects.get_or_create(
            code=microdistrict_code,
            defaults={
                'name': 'По умолчанию',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created microdistrict: {microdistrict.name}')
            )

        # Import housing complexes
        created_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            try:
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    
                    for row_num, row in enumerate(reader, 1):
                        if not row or not row[0].strip():
                            continue
                            
                        complex_name = row[0].strip()
                        
                        # Skip if already exists
                        if ResidentialComplex.objects.filter(name=complex_name).exists():
                            skipped_count += 1
                            self.stdout.write(f'Skipped existing: {complex_name}')
                            continue
                        
                        # Create new residential complex
                        ResidentialComplex.objects.create(
                            name=complex_name,
                            microdistrict=microdistrict,
                            is_active=True
                        )
                        created_count += 1
                        
                        if created_count % 100 == 0:
                            self.stdout.write(f'Processed {created_count} complexes...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error reading file: {str(e)}')
                )
                return

        # Final results
        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed!\n'
                f'Created: {created_count} housing complexes\n'
                f'Skipped: {skipped_count} existing complexes\n'
                f'Microdistrict: {microdistrict.name}'
            )
        ) 
import json
from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
from django.apps import apps


class Command(BaseCommand):
    help = 'Import reference data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default='reference_data.json',
            help='Input JSON file path (default: reference_data.json)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing reference data before import'
        )

    def handle(self, *args, **options):
        input_file = options['input']
        clear_existing = options['clear']
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File {input_file} not found!')
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading file: {str(e)}')
            )
            return

        if clear_existing:
            self.stdout.write('Clearing existing reference data...')
            # Clear in reverse order due to foreign keys
            from main.models import (
                ResidentialComplex, Agency, Landmark, 
                BuildingType, RepairType, Microdistrict
            )
            
            with transaction.atomic():
                ResidentialComplex.objects.all().delete()
                Agency.objects.all().delete()
                Landmark.objects.all().delete()
                BuildingType.objects.all().delete()
                RepairType.objects.all().delete()
                Microdistrict.objects.all().delete()
            
            self.stdout.write('Existing reference data cleared.')

        # Import data
        self.stdout.write(f'Importing {len(data)} objects...')
        
        success_count = 0
        error_count = 0
        
        with transaction.atomic():
            try:
                # Convert back to JSON for deserializer
                json_data = json.dumps(data)
                
                for deserialized_object in serializers.deserialize('json', json_data):
                    try:
                        deserialized_object.save()
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'Error importing object: {str(e)}'
                            )
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Critical error during import: {str(e)}')
                )
                return

        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed!\n'
                f'Successfully imported: {success_count} objects\n'
                f'Errors: {error_count} objects'
            )
        ) 
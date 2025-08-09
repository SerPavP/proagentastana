import json
from django.core.management.base import BaseCommand
from django.core import serializers
from main.models import (
    Microdistrict, ResidentialComplex, RepairType, 
    BuildingType, Landmark, Agency
)


class Command(BaseCommand):
    help = 'Export reference data to JSON file (excluding user data like collections, announcements, users)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='reference_data.json',
            help='Output JSON file path (default: reference_data.json)'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        # Define models to export (reference data only)
        models_to_export = [
            Microdistrict,
            RepairType,
            BuildingType,
            Landmark,
            Agency,
            ResidentialComplex,  # Export this last because of foreign key to Microdistrict
        ]
        
        all_data = []
        total_objects = 0
        
        for model in models_to_export:
            objects = model.objects.all()
            count = objects.count()
            
            if count > 0:
                serialized_data = serializers.serialize('json', objects)
                parsed_data = json.loads(serialized_data)
                all_data.extend(parsed_data)
                total_objects += count
                
                self.stdout.write(f'Exported {count} {model.__name__} objects')
            else:
                self.stdout.write(f'No {model.__name__} objects found')
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully exported {total_objects} reference objects to {output_file}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error writing to file: {str(e)}')
            ) 
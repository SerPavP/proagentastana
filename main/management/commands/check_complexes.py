from django.core.management.base import BaseCommand
from main.models import ResidentialComplex, Microdistrict


class Command(BaseCommand):
    help = 'Check imported housing complexes'

    def handle(self, *args, **options):
        total_complexes = ResidentialComplex.objects.count()
        total_microdistricts = Microdistrict.objects.count()
        
        self.stdout.write(f'Total housing complexes: {total_complexes}')
        self.stdout.write(f'Total microdistricts: {total_microdistricts}')
        
        self.stdout.write('\nSample complexes:')
        for complex in ResidentialComplex.objects.all()[:10]:
            self.stdout.write(f'- {complex.name} (Microdistrict: {complex.microdistrict.name})')
        
        self.stdout.write('\nRussian language complexes:')
        russian_complexes = ResidentialComplex.objects.filter(
            name__regex=r'[а-яё]'
        )[:5]
        for complex in russian_complexes:
            self.stdout.write(f'- {complex.name}')
        
        self.stdout.write(f'\nTotal Russian complexes: {russian_complexes.count()}') 
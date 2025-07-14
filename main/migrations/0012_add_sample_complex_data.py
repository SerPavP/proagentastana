from django.db import migrations

def add_sample_complex_data(apps, schema_editor):
    Address = apps.get_model('main', 'Address')
    
    # Создаем несколько тестовых адресов с жилыми комплексами
    sample_addresses = [
        {
            'microdistrict': 'almaty',
            'complex_name': 'Хигрин Астана',
            'street': 'Кошкарбаева',
            'building_no': '8',
        },
        {
            'microdistrict': 'esil',
            'complex_name': 'Изумрудный город',
            'street': 'Кабанбай батыра',
            'building_no': '15',
        },
        {
            'microdistrict': 'saryarka',
            'complex_name': 'Академик Резиденс',
            'street': 'Академика Павлова',
            'building_no': '42',
        },
        {
            'microdistrict': 'nura',
            'complex_name': 'Нурлы Тау',
            'street': 'Сыганак',
            'building_no': '20',
        },
        {
            'microdistrict': 'almaty',
            'complex_name': 'Атамекен',
            'street': 'Бейбітшілік',
            'building_no': '5',
        },
        {
            'microdistrict': 'esil',
            'complex_name': 'Авиценна',
            'street': 'Авиценна',
            'building_no': '1',
        },
        {
            'microdistrict': 'saryarka',
            'complex_name': 'Comfort City',
            'street': 'Бараева',
            'building_no': '33',
        },
        {
            'microdistrict': 'almaty',
            'complex_name': 'Северное сияние',
            'street': 'Кошкарбаева',
            'building_no': '25',
        },
        {
            'microdistrict': 'esil',
            'complex_name': 'Гран-при',
            'street': 'Динмухамеда Кунаева',
            'building_no': '12',
        },
        {
            'microdistrict': 'nura',
            'complex_name': 'Алтын Орда',
            'street': 'Алтын Орда',
            'building_no': '18',
        },
        {
            'microdistrict': 'saryarka',
            'complex_name': 'Астана Аparts',
            'street': 'Манаса',
            'building_no': '24',
        },
        {
            'microdistrict': 'almaty',
            'complex_name': 'Премиум Плаза',
            'street': 'Амангельды Иманова',
            'building_no': '7',
        },
    ]
    
    for address_data in sample_addresses:
        Address.objects.get_or_create(**address_data)

def reverse_add_sample_complex_data(apps, schema_editor):
    # Обратная миграция - удаление созданных данных
    Address = apps.get_model('main', 'Address')
    
    complex_names = [
        'Хигрин Астана', 'Изумрудный город', 'Академик Резиденс', 'Нурлы Тау',
        'Атамекен', 'Авиценна', 'Comfort City', 'Северное сияние', 'Гран-при',
        'Алтын Орда', 'Астана Аparts', 'Премиум Плаза'
    ]
    
    Address.objects.filter(complex_name__in=complex_names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_landmark_remove_announcement_landmark_and_more'),
    ]

    operations = [
        migrations.RunPython(add_sample_complex_data, reverse_add_sample_complex_data),
    ] 
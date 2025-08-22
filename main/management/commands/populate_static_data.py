from django.core.management.base import BaseCommand
from main.models import Microdistrict, RepairType, BuildingType, ResidentialComplex, Landmark


class Command(BaseCommand):
    help = 'Populate static data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение статических данных...')
        
        # Создаем микрорайоны
        self.create_microdistricts()
        
        # Создаем типы ремонта
        self.create_repair_types()
        
        # Создаем типы домов
        self.create_building_types()
        
        # Создаем достопримечательности
        self.create_landmarks()
        
        # Создаем жилые комплексы (небольшая выборка)
        self.create_residential_complexes()
        
        self.stdout.write(
            self.style.SUCCESS('Статические данные успешно созданы!')
        )

    def create_microdistricts(self):
        """Создание микрорайонов"""
        microdistricts = [
            'Алматы р-н',
            'Байконур р-н', 
            'Есильский р-н',
            'Нура р-н',
            'Сарайшик р-н',
            'Сарыарка р-н',
        ]
        
        for name in microdistricts:
            microdistrict, created = Microdistrict.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'Создан микрорайон: {name}')
            else:
                self.stdout.write(f'Микрорайон уже существует: {name}')

    def create_repair_types(self):
        """Создание типов ремонта"""
        repair_types = [
            'Новый ремонт',
            'Не новый, но аккуратный ремонт',
            'Старый ремонт',
            'Черновая отделка',
        ]
        
        for name in repair_types:
            repair_type, created = RepairType.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'Создан тип ремонта: {name}')
            else:
                self.stdout.write(f'Тип ремонта уже существует: {name}')

    def create_building_types(self):
        """Создание типов домов"""
        building_types = [
            'Кирпичный',
            'Монолитный',
            'Панельный',
            'Иной',
        ]
        
        for name in building_types:
            building_type, created = BuildingType.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'Создан тип дома: {name}')
            else:
                self.stdout.write(f'Тип дома уже существует: {name}')

    def create_landmarks(self):
        """Создание достопримечательностей"""
        landmarks = [
            ('abu_dhabi_baiterek', 'Абу Даби Плаза и Байтерек'),
            ('barys_astana_arena', 'Барыс Арена и Астана Арена'),
            ('botanical_garden', 'Ботанический сад'),
            ('akimat_building', 'Здание акимата (Музей первого Президента)'),
            ('nazarbayev_university', 'Назарбаев Университет'),
            ('new_railway_station', 'Новый вокзал'),
            ('koktal_park', 'Парк "Коктал"'),
            ('pyramid', 'Пирамида'),
            ('presidential_park_left', 'Президентский парк (Левый берег)'),
            ('presidential_park_right', 'Президентский парк (Правый берег)'),
            ('artem_market', 'Рынок Артём'),
            ('old_railway_station', 'Старый вокзал'),
            ('sphere_park', 'Сфера Парк'),
            ('ellington_mall', 'ТРК "Эллингтон Молл"'),
            ('eurasian_mall', 'ТРЦ "Евразия"'),
            ('meeting_mall', 'ТЦ "Встреча"'),
            ('triathlon_park', 'Триатлон Парк'),
            ('khan_shatyr', 'Хан Шатыр'),
            ('central_mosque', 'Центральная (Новая) Мечеть'),
            ('central_embankment', 'Центральная набережная'),
            ('central_park', 'Центральный парк'),
            ('expo_mega', 'ЭКСПО и ТРЦ "MEGA Silkway"'),
        ]
        
        for code, name in landmarks:
            landmark, created = Landmark.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            if created:
                self.stdout.write(f'Создана достопримечательность: {name}')
            else:
                self.stdout.write(f'Достопримечательность уже существует: {name}')

    def create_residential_complexes(self):
        """Создание популярных жилых комплексов"""
        # Получаем микрорайоны для распределения ЖК
        microdistricts = list(Microdistrict.objects.all())
        if not microdistricts:
            self.stdout.write(self.style.ERROR('Не найдены микрорайоны. Создайте их сначала.'))
            return
            
        # ЖК с привязкой к конкретным микрорайонам
        complexes_by_district = {
            'Есильский р-н': [
                'Абай-2', 'Авиценна', 'Астана сити', 'Ак Булак', 'Алматау',
                'Алтын Орда', 'Берекет', 'Гранд Астана', 'Есиль', 'Жагалау'
            ],
            'Сарыарка р-н': [
                'Байконур', 'Бухар Жырау', 'Градокомплекс', 'Жас Канат', 
                'Жасыл ел', 'Железнодорожный', 'Изумруд', 'Кайнар'
            ],
            'Алматы р-н': [
                'Коркем', 'ЛЕЯ', 'Мангилик Ел', 'Мерей', 'Микрорайон Самал',
                'Нур Астана', 'Орбита', 'Отырар'
            ],
            'Байконур р-н': [
                'Памир', 'Престиж', 'Сарыарка', 'Триумф', 'Туран'
            ],
            'Нура р-н': [
                'Улытау', 'Хайтек Сити', 'Центральный'
            ],
            'Сарайшик р-н': [
                'Шанырак'
            ]
        }
        
        for district_name, complex_names in complexes_by_district.items():
            try:
                microdistrict = Microdistrict.objects.get(name=district_name)
                for name in complex_names:
                    complex_obj, created = ResidentialComplex.objects.get_or_create(
                        name=name,
                        defaults={
                            'is_active': True,
                            'microdistrict': microdistrict
                        }
                    )
                    if created:
                        self.stdout.write(f'Создан ЖК: {name} в {district_name}')
                    else:
                        self.stdout.write(f'ЖК уже существует: {name}')
            except Microdistrict.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Микрорайон {district_name} не найден')
                ) 
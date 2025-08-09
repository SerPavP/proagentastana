from django.core.cache import cache
from django.core.management.base import BaseCommand
import time

class Command(BaseCommand):
    help = 'Управление кэшем статических данных (микрорайоны, типы домов и т.д.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить весь кэш статических данных'
        )
        parser.add_argument(
            '--warmup',
            action='store_true',
            help='Прогреть кэш статических данных'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Показать статистику кэша'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Протестировать производительность кэширования'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_static_cache()
        elif options['warmup']:
            self.warmup_static_cache()
        elif options['stats']:
            self.show_cache_stats()
        elif options['test']:
            self.test_cache_performance()
        else:
            self.stdout.write(
                self.style.WARNING('Укажите действие: --clear, --warmup, --stats или --test')
            )

    def clear_static_cache(self):
        """Очищает кэш статических данных"""
        self.stdout.write('🗑️ Очистка кэша статических данных...')
        
        # Ключи кэша для форм поиска
        search_keys = [
            'search_form_microdistrict_choices_v2',
            'search_form_building_type_choices_v2',
            'search_form_complex_choices_v2',
        ]
        
        # Ключи кэша для форм объявлений
        announcement_keys = [
            'announcement_form_microdistrict_qs_v2',
            'announcement_form_complex_qs_v2',
            'announcement_form_repair_qs_v2',
            'announcement_form_building_type_qs_v2',
        ]
        
        all_keys = search_keys + announcement_keys
        
        for key in all_keys:
            cache.delete(key)
            self.stdout.write(f'   ❌ Удален: {key}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Очищено {len(all_keys)} ключей кэша')
        )

    def warmup_static_cache(self):
        """Прогревает кэш статических данных"""
        self.stdout.write('🔥 Прогрев кэша статических данных...')
        
        start_time = time.time()
        
        try:
            # Импортируем формы для инициализации кэша
            from main.forms import SearchForm, AnnouncementForm
            
            # Создаем формы - это автоматически заполнит кэш
            search_form = SearchForm()
            self.stdout.write('   ✅ SearchForm кэш прогрет')
            
            announcement_form = AnnouncementForm()
            self.stdout.write('   ✅ AnnouncementForm кэш прогрет')
            
            elapsed = time.time() - start_time
            self.stdout.write(
                self.style.SUCCESS(f'🚀 Кэш прогрет за {elapsed:.2f} секунд')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка прогрева кэша: {e}')
            )

    def show_cache_stats(self):
        """Показывает статистику кэша с учетом LocMemCache"""
        self.stdout.write('📊 Статистика кэша статических данных:')
        self.stdout.write('')
        
        # Объясняем поведение LocMemCache
        from django.conf import settings
        cache_backend = settings.CACHES['default']['BACKEND']
        
        if 'locmem' in cache_backend.lower():
            self.stdout.write(self.style.WARNING('⚠️ Используется LocMemCache (память процесса)'))
            self.stdout.write('   Кэш привязан к конкретному процессу Python')
            self.stdout.write('   Команда stats запускается в НОВОМ процессе')
            self.stdout.write('   Поэтому кэш всегда будет показываться как пустой')
            self.stdout.write('')
        
        # Проверяем и прогреваем кэш в этом же процессе
        self.stdout.write('🔥 Проверяем кэш в текущем процессе...')
        
        try:
            from main.forms import SearchForm, AnnouncementForm
            
            # Очищаем для чистого теста
            cache.clear()
            self.stdout.write('   🧹 Кэш очищен')
            
            # Создаем формы
            search_form = SearchForm()
            announcement_form = AnnouncementForm()
            
            # Проверяем что кэш заполнился
            cache_keys = [
                ('SearchForm микрорайоны', 'search_form_microdistrict_choices_v2'),
                ('SearchForm типы домов', 'search_form_building_type_choices_v2'),
                ('SearchForm ЖК', 'search_form_complex_choices_v2'),
                ('AnnouncementForm микрорайоны', 'announcement_form_microdistrict_qs_v2'),
                ('AnnouncementForm ЖК', 'announcement_form_complex_qs_v2'),
                ('AnnouncementForm ремонт', 'announcement_form_repair_qs_v2'),
                ('AnnouncementForm типы домов', 'announcement_form_building_type_qs_v2'),
            ]
            
            cached_count = 0
            total_count = len(cache_keys)
            
            for name, key in cache_keys:
                value = cache.get(key)
                if value is not None:
                    if isinstance(value, list) and len(value) > 0:
                        first_item = value[0]
                        if isinstance(first_item, tuple):
                            # Choices для форм поиска
                            self.stdout.write(f'   ✅ {name}: {len(value)-1} вариантов (+ пустой)')
                        else:
                            # Объекты Django для форм объявлений
                            self.stdout.write(f'   ✅ {name}: {len(value)} объектов')
                    else:
                        self.stdout.write(f'   ✅ {name}: кэшировано')
                    cached_count += 1
                else:
                    self.stdout.write(f'   ❌ {name}: не кэшировано')
            
            self.stdout.write('')
            if cached_count == total_count:
                self.stdout.write(self.style.SUCCESS(f'🎉 Кэширование работает отлично! ({cached_count}/{total_count})'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Проблемы с кэшированием ({cached_count}/{total_count})'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка проверки кэша: {e}'))

    def test_cache_performance(self):
        """Тестирует производительность кэширования"""
        self.stdout.write('⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ КЭШИРОВАНИЯ')
        self.stdout.write('=' * 55)
        
        try:
            from main.forms import SearchForm, AnnouncementForm
            
            # Очищаем кэш
            cache.clear()
            
            # Тест без кэша (первый запуск)
            self.stdout.write('🐌 БЕЗ КЭША (первый запуск):')
            start = time.time()
            form1 = SearchForm()
            time1 = time.time() - start
            self.stdout.write(f'   SearchForm: {time1:.3f} сек')

            start = time.time()
            form2 = AnnouncementForm()
            time2 = time.time() - start
            self.stdout.write(f'   AnnouncementForm: {time2:.3f} сек')

            total_without_cache = time1 + time2
            self.stdout.write(f'   📊 ИТОГО: {total_without_cache:.3f} сек')
            self.stdout.write('')

            # Тест с кэшем (повторные запуски)
            self.stdout.write('🚀 С КЭШЕМ (повторные запуски):')
            start = time.time()
            form3 = SearchForm()
            time3 = time.time() - start
            self.stdout.write(f'   SearchForm: {time3:.3f} сек')

            start = time.time()
            form4 = AnnouncementForm()
            time4 = time.time() - start
            self.stdout.write(f'   AnnouncementForm: {time4:.3f} сек')

            total_with_cache = time3 + time4
            self.stdout.write(f'   📊 ИТОГО: {total_with_cache:.3f} сек')
            self.stdout.write('')

            # Сравнение
            if total_without_cache > 0 and total_with_cache > 0:
                speedup = total_without_cache / total_with_cache
                improvement = ((total_without_cache - total_with_cache) / total_without_cache) * 100
                
                self.stdout.write('🎯 РЕЗУЛЬТАТ:')
                self.stdout.write(f'   Ускорение: {speedup:.1f}x')
                self.stdout.write(f'   Улучшение: {improvement:.1f}%')
                
                if speedup > 10:
                    self.stdout.write(self.style.SUCCESS('   ✅ НЕВЕРОЯТНОЕ ускорение!'))
                elif speedup > 2:
                    self.stdout.write(self.style.SUCCESS('   ✅ ОТЛИЧНОЕ ускорение!'))
                elif speedup > 1.5:
                    self.stdout.write(self.style.SUCCESS('   ✅ Хорошее ускорение!'))
                else:
                    self.stdout.write(self.style.WARNING('   ⚠️ Небольшое ускорение'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка тестирования: {e}'))

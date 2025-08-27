#!/usr/bin/env python
"""
Скрипт для полного удаления пользователя и всех его данных
Использование:
    python user_delete.py +79999999999  # Удалить пользователя полностью
"""

import os
import sys
import django
import argparse
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proagentastana.settings')
django.setup()

from main.models import User, Announcement, Collection, CollectionItem, UserSession, UserPhoto

def format_phone(phone):
    """Форматирует номер телефона в стандартный вид"""
    # Убираем все нецифровые символы
    digits = ''.join(filter(str.isdigit, phone))
    
    # Если номер начинается с 8, заменяем на 7
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    
    # Если номер начинается с 9, добавляем 7
    if digits.startswith('9'):
        digits = '7' + digits
    
    # Добавляем + если его нет
    if not phone.startswith('+'):
        phone = '+' + digits
    
    return phone

def find_user_by_phone(phone):
    """Находит пользователя по номеру телефона"""
    formatted_phone = format_phone(phone)
    
    try:
        user = User.objects.get(phone=formatted_phone)
        return user
    except User.DoesNotExist:
        return None

def get_user_statistics(user):
    """Получает статистику пользователя"""
    announcements_count = Announcement.objects.filter(user=user).count()
    collections_count = Collection.objects.filter(user=user).count()
    sessions_count = UserSession.objects.filter(user=user).count()
    photos_count = UserPhoto.objects.filter(user=user).count()
    
    # Подсчитываем объявления в коллекциях других пользователей
    collection_entries_count = CollectionItem.objects.filter(
        announcement__user=user
    ).count()
    
    return {
        'announcements': announcements_count,
        'collections': collections_count,
        'sessions': sessions_count,
        'photos': photos_count,
        'collection_entries': collection_entries_count
    }

def delete_user_completely(user):
    """Полностью удаляет пользователя и все его данные"""
    stats = get_user_statistics(user)
    
    print(f"🗑️  Начинаю удаление пользователя {user.phone}...")
    print(f"   👤 {user.first_name} {user.last_name}")
    
    # 1. Удаляем объявления из коллекций других пользователей
    if stats['collection_entries'] > 0:
        print(f"   📚 Удаляю {stats['collection_entries']} записей из коллекций...")
        CollectionItem.objects.filter(announcement__user=user).delete()
    
    # 2. Удаляем объявления пользователя (это также удалит связанные фото)
    if stats['announcements'] > 0:
        print(f"   🏠 Удаляю {stats['announcements']} объявлений...")
        Announcement.objects.filter(user=user).delete()
    
    # 3. Удаляем коллекции пользователя
    if stats['collections'] > 0:
        print(f"   📚 Удаляю {stats['collections']} коллекций...")
        Collection.objects.filter(user=user).delete()
    
    # 4. Удаляем сессии пользователя
    if stats['sessions'] > 0:
        print(f"   🔄 Удаляю {stats['sessions']} сессий...")
        UserSession.objects.filter(user=user).delete()
    
    # 5. Удаляем фото профиля пользователя
    if stats['photos'] > 0:
        print(f"   📸 Удаляю {stats['photos']} фото профиля...")
        UserPhoto.objects.filter(user=user).delete()
    
    # 6. Удаляем самого пользователя
    user_phone = user.phone
    user_name = f"{user.first_name} {user.last_name}"
    user.delete()
    
    print(f"✅ Пользователь {user_phone} полностью удален!")
    print(f"   👤 {user_name}")
    print(f"   📞 {user_phone}")
    print(f"   🗑️  Удалено записей: {sum(stats.values())}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Полное удаление пользователя и всех его данных',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  ВНИМАНИЕ: Это действие необратимо!
Будут удалены:
- Все объявления пользователя
- Все коллекции пользователя  
- Все сессии пользователя
- Все фото пользователя
- Записи объявлений в коллекциях других пользователей
- Сам пользователь

Примеры использования:
  python user_delete.py +79999999999    # Удалить пользователя
  python user_delete.py 79999999999     # Работает с разными форматами
  python user_delete.py +79999999999 -c # Подтвердить без запроса
        """
    )
    
    parser.add_argument('phone', help='Номер телефона пользователя')
    parser.add_argument('-c', '--confirm', action='store_true', 
                       help='Подтвердить удаление без запроса')
    
    args = parser.parse_args()
    
    print(f"🔍 Поиск пользователя с номером: {args.phone}")
    
    # Ищем пользователя
    user = find_user_by_phone(args.phone)
    
    if not user:
        print(f"❌ Пользователь с номером {args.phone} не найден!")
        print("💡 Проверьте правильность номера телефона")
        sys.exit(1)
    
    # Показываем информацию о пользователе
    stats = get_user_statistics(user)
    
    print(f"\n📱 Информация о пользователе:")
    print(f"   👤 Имя: {user.first_name} {user.last_name}")
    print(f"   📞 Телефон: {user.phone}")
    print(f"   🏢 Агентство: {user.agency.name if user.agency else 'Не указано'}")
    print(f"   🔑 Активен: {'✅ Да' if user.is_active else '❌ Нет'}")
    print(f"   📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y %H:%M')}")
    
    print(f"\n📊 Статистика данных для удаления:")
    print(f"   🏠 Объявлений: {stats['announcements']}")
    print(f"   📚 Коллекций: {stats['collections']}")
    print(f"   🔄 Сессий: {stats['sessions']}")
    print(f"   📸 Фото профиля: {stats['photos']}")
    print(f"   📋 Записей в коллекциях: {stats['collection_entries']}")
    print(f"   📈 Всего записей: {sum(stats.values())}")
    
    # Запрашиваем подтверждение
    if not args.confirm:
        print(f"\n⚠️  ВНИМАНИЕ: Это действие НЕОБРАТИМО!")
        print(f"   Все данные пользователя будут удалены навсегда!")
        confirm = input("Продолжить удаление? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', 'да', 'д']:
            print("❌ Операция отменена пользователем")
            sys.exit(0)
        
        # Дополнительное подтверждение
        print(f"\n⚠️  ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ:")
        print(f"   Вы уверены, что хотите удалить пользователя {user.phone}?")
        final_confirm = input("Введите 'DELETE' для подтверждения: ").strip()
        
        if final_confirm != 'DELETE':
            print("❌ Операция отменена - неправильное подтверждение")
            sys.exit(0)
    
    # Удаляем пользователя
    print(f"\n🗑️  Начинаю удаление...")
    delete_user_completely(user)
    
    print(f"\n✅ Операция завершена успешно!")
    print(f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

if __name__ == "__main__":
    main() 
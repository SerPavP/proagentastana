#!/usr/bin/env python
"""
Скрипт для сброса пароля пользователя
Использование:
    python password_reset.py +79999999999  # Сбросить пароль на 11223344
"""

import os
import sys
import django
import argparse
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proagentastana.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from main.models import User

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

def reset_user_password(user):
    """Сбрасывает пароль пользователя на 11223344"""
    new_password = "11223344"
    user.password = make_password(new_password)
    user.save()
    
    print(f"✅ Пароль успешно сброшен для пользователя {user.phone}")
    print(f"   👤 {user.first_name} {user.last_name}")
    print(f"   📞 {user.phone}")
    print(f"   🔑 Новый пароль: {new_password}")
    print(f"   🔗 Может войти на: http://127.0.0.1:8000/login/")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Сброс пароля пользователя на 11223344',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python password_reset.py +79999999999    # Сбросить пароль
  python password_reset.py 79999999999     # Работает с разными форматами
  python password_reset.py 89999999999     # Автоматически заменит 8 на 7
  python password_reset.py 9999999999      # Автоматически добавит +7
        """
    )
    
    parser.add_argument('phone', help='Номер телефона пользователя')
    parser.add_argument('-c', '--confirm', action='store_true', 
                       help='Подтвердить сброс пароля без запроса')
    
    args = parser.parse_args()
    
    print(f"🔍 Поиск пользователя с номером: {args.phone}")
    
    # Ищем пользователя
    user = find_user_by_phone(args.phone)
    
    if not user:
        print(f"❌ Пользователь с номером {args.phone} не найден!")
        print("💡 Проверьте правильность номера телефона")
        sys.exit(1)
    
    # Показываем информацию о пользователе
    print(f"\n📱 Информация о пользователе:")
    print(f"   👤 Имя: {user.first_name} {user.last_name}")
    print(f"   📞 Телефон: {user.phone}")
    print(f"   🏢 Агентство: {user.agency.name if user.agency else 'Не указано'}")
    print(f"   🔑 Активен: {'✅ Да' if user.is_active else '❌ Нет'}")
    
    # Запрашиваем подтверждение
    if not args.confirm:
        print(f"\n⚠️  ВНИМАНИЕ: Пароль будет сброшен на '11223344'")
        confirm = input("Продолжить? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', 'да', 'д']:
            print("❌ Операция отменена пользователем")
            sys.exit(0)
    
    # Сбрасываем пароль
    print(f"\n🔧 Сброс пароля...")
    reset_user_password(user)
    
    print(f"\n✅ Операция завершена успешно!")
    print(f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

if __name__ == "__main__":
    main() 
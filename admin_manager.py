#!/usr/bin/env python
"""
Скрипт для управления правами администратора пользователей
Использование:
    python admin_manager.py +79999999999 -T  # Дать права администратора
    python admin_manager.py +79999999999 -F  # Убрать права администратора
    python admin_manager.py +79999999999 -S  # Показать статус пользователя
"""

import os
import sys
import django
import argparse
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proagentastana.settings')
django.setup()

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

def show_user_status(user):
    """Показывает статус пользователя"""
    print(f"\n📱 Информация о пользователе:")
    print(f"   👤 Имя: {user.first_name} {user.last_name}")
    print(f"   📞 Телефон: {user.phone}")
    print(f"   🏢 Агентство: {user.agency.name if user.agency else 'Не указано'}")
    print(f"   🔑 Активен: {'✅ Да' if user.is_active else '❌ Нет'}")
    print(f"   👨‍💼 Staff: {'✅ Да' if user.is_staff else '❌ Нет'}")
    print(f"   👑 Суперпользователь: {'✅ Да' if user.is_superuser else '❌ Нет'}")
    print(f"   📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y %H:%M')}")
    print(f"   🔄 Последнее обновление: {user.updated_at.strftime('%d.%m.%Y %H:%M')}")

def grant_admin_rights(user):
    """Дает права администратора пользователю"""
    if user.is_staff and user.is_superuser:
        print(f"⚠️  Пользователь {user.phone} уже имеет права администратора!")
        return False
    
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    print(f"✅ Права администратора успешно выданы пользователю {user.phone}")
    print(f"   👤 {user.first_name} {user.last_name}")
    print(f"   📞 {user.phone}")
    print(f"   🔑 Теперь может войти в админку: http://127.0.0.1:8000/admin/")
    
    return True

def revoke_admin_rights(user):
    """Убирает права администратора у пользователя"""
    if not user.is_staff and not user.is_superuser:
        print(f"⚠️  Пользователь {user.phone} не имеет прав администратора!")
        return False
    
    user.is_staff = False
    user.is_superuser = False
    user.save()
    
    print(f"✅ Права администратора успешно убраны у пользователя {user.phone}")
    print(f"   👤 {user.first_name} {user.last_name}")
    print(f"   📞 {user.phone}")
    print(f"   🔑 Больше не может войти в админку")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Управление правами администратора пользователей',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python admin_manager.py +79999999999 -T    # Дать права администратора
  python admin_manager.py +79999999999 -F    # Убрать права администратора
  python admin_manager.py +79999999999 -S    # Показать статус пользователя
  python admin_manager.py 89999999999 -T     # Работает с разными форматами
  python admin_manager.py 9999999999 -T      # Автоматически добавляет +7
        """
    )
    
    parser.add_argument('phone', help='Номер телефона пользователя')
    parser.add_argument('-T', '--grant', action='store_true', 
                       help='Дать права администратора (True)')
    parser.add_argument('-F', '--revoke', action='store_true', 
                       help='Убрать права администратора (False)')
    parser.add_argument('-S', '--status', action='store_true', 
                       help='Показать статус пользователя')
    
    args = parser.parse_args()
    
    # Проверяем, что указан хотя бы один флаг
    if not any([args.grant, args.revoke, args.status]):
        print("❌ Ошибка: Необходимо указать действие (-T, -F или -S)")
        parser.print_help()
        sys.exit(1)
    
    # Проверяем, что указан только один флаг
    flags_count = sum([args.grant, args.revoke, args.status])
    if flags_count > 1:
        print("❌ Ошибка: Можно указать только одно действие за раз")
        sys.exit(1)
    
    print(f"🔍 Поиск пользователя с номером: {args.phone}")
    
    # Ищем пользователя
    user = find_user_by_phone(args.phone)
    
    if not user:
        print(f"❌ Пользователь с номером {args.phone} не найден!")
        print("💡 Проверьте правильность номера телефона")
        sys.exit(1)
    
    # Выполняем действие
    if args.status:
        show_user_status(user)
    
    elif args.grant:
        print(f"🔧 Выдача прав администратора...")
        grant_admin_rights(user)
    
    elif args.revoke:
        print(f"🔧 Удаление прав администратора...")
        revoke_admin_rights(user)
    
    print(f"\n✅ Операция завершена успешно!")
    print(f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

if __name__ == "__main__":
    main() 
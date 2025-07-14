#!/usr/bin/env python
"""
Скрипт для создания или изменения пользователя на супер-админа
"""
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proagentastana.settings')
django.setup()

from main.models import User, Agency

def make_superuser(phone_number):
    """Делает пользователя супер-админом"""
    try:
        user = User.objects.get(phone=phone_number)
        print(f'✅ Пользователь найден: {user.first_name} {user.last_name} ({user.phone})')
        
        # Делаем его супер-админом
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print('🎉 Пользователь успешно сделан супер-админом!')
        print(f'   - is_superuser: {user.is_superuser}')
        print(f'   - is_staff: {user.is_staff}')
        print(f'   - is_active: {user.is_active}')
        return True
        
    except User.DoesNotExist:
        print(f'❌ Пользователь с номером {phone_number} не найден в базе данных')
        return False

def list_all_users():
    """Показывает всех пользователей в системе"""
    print('\n📋 Все пользователи в системе:')
    users = User.objects.all()
    if users:
        for user in users:
            admin_status = "Супер-админ" if user.is_superuser else "Обычный пользователь"
            print(f'   - {user.phone} ({user.first_name} {user.last_name}) - {admin_status}')
    else:
        print('   Пользователи не найдены')

def create_superuser(phone_number, first_name, last_name, password):
    """Создает нового супер-пользователя"""
    try:
        # Проверяем, есть ли агентство по умолчанию
        agency = Agency.objects.first()
        if not agency:
            print('❌ Не найдено ни одного агентства. Создайте агентство сначала.')
            return False
        
        user = User.objects.create_superuser(
            phone=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=password,
            agency=agency
        )
        
        print(f'✅ Супер-пользователь создан: {user.first_name} {user.last_name} ({user.phone})')
        print(f'   - Агентство: {user.agency.name}')
        print(f'   - Пароль: {password}')
        return True
        
    except Exception as e:
        print(f'❌ Ошибка создания пользователя: {e}')
        return False

if __name__ == '__main__':
    phone = '+71111111111'
    
    print('🔧 Скрипт управления супер-админами')
    print('=' * 40)
    
    # Сначала показываем всех пользователей
    list_all_users()
    
    print(f'\n🎯 Делаем пользователя {phone} супер-админом...')
    
    if make_superuser(phone):
        print('\n✅ Задача выполнена успешно!')
    else:
        print(f'\n❓ Пользователь не найден. Создать нового супер-пользователя с номером {phone}?')
        print('💡 Если да, то будет создан пользователь:')
        print(f'   - Телефон: {phone}')
        print(f'   - Имя: SuperAdmin')
        print(f'   - Фамилия: User')
        print(f'   - Пароль: admin123')
        
        # Создаем нового супер-пользователя
        if create_superuser(phone, 'SuperAdmin', 'User', 'admin123'):
            print('\n✅ Новый супер-пользователь создан!')
        else:
            print('\n❌ Не удалось создать супер-пользователя')
    
    print('\n📊 Финальное состояние пользователей:')
    list_all_users()
    
    print('\n🌐 Информация для входа в админ панель:')
    print('   URL: http://127.0.0.1:8000/admin/')
    print(f'   Логин: {phone}')
    print('   Пароль: admin123 (если был создан новый пользователь)')
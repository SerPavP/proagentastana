#!/usr/bin/env python
"""
Быстрая настройка проекта для работы с Neon Database
"""
import os
import sys
import subprocess

def create_env_template():
    """Создаёт шаблон .env файла если его нет"""
    if os.path.exists('.env'):
        print("✅ Файл .env уже существует")
        return True
    
    env_template = """# Neon Database Configuration
DATABASE_URL=postgresql://username:password@hostname/database_name?sslmode=require

# Django Configuration  
SECRET_KEY=your-secret-key-here
DEBUG=True

# Optional for production
# ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
# CSRF_TRUSTED_ORIGINS=https://yourdomain.com
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_template)
        print("✅ Создан шаблон .env файла")
        print("📝 Не забудьте обновить DATABASE_URL и SECRET_KEY!")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания .env файла: {e}")
        return False

def install_requirements():
    """Устанавливает зависимости"""
    try:
        print("📦 Установка зависимостей...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        print(f"Детали: {e.stderr}")
        return False

def run_migrations():
    """Применяет миграции с автоматическим исправлением проблем"""
    try:
        print("🔄 Создание миграций...")
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                      check=True, capture_output=True, text=True)
        
        print("🔄 Применение миграций с исправлением проблем...")
        result = subprocess.run([sys.executable, 'fix_migrations.py'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Миграции применены")
            return True
        else:
            print(f"❌ Ошибка применения миграций")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания миграций: {e}")
        print(f"Детали: {e.stderr}")
        return False

def check_connection():
    """Проверяет подключение к БД"""
    try:
        print("🔍 Проверка подключения к базе данных...")
        result = subprocess.run([sys.executable, 'check_db_connection.py'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Подключение к базе данных работает!")
            return True
        else:
            print("❌ Проблема с подключением к базе данных")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки подключения: {e}")
        return False

def main():
    print("🚀 Настройка проекта для работы с Neon Database\n")
    
    steps = [
        ("Создание .env файла", create_env_template),
        ("Установка зависимостей", install_requirements),
        ("Применение миграций", run_migrations),
        ("Проверка подключения", check_connection),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"\n❌ Ошибка на этапе: {step_name}")
            print("🔧 Проверьте настройки и попробуйте снова")
            return False
    
    print("\n🎉 Настройка завершена успешно!")
    print("\n📚 Следующие шаги:")
    print("1. Обновите DATABASE_URL в файле .env")
    print("2. Обновите SECRET_KEY в файле .env")
    print("3. Запустите сервер: python manage.py runserver")
    print("\n📖 Подробная документация: neon_setup_guide.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
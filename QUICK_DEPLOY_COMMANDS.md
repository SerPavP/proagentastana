# 🚀 Быстрые команды для развертывания

## Windows → GitHub
```bash
cd "C:\Users\KOT_CAT\Desktop\Projectssss\curs\Выкалыдвание на сайты\proagentastana"
git add .
git commit -m "Initial commit: Django real estate project"
git remote add origin https://github.com/YOUR_USERNAME/proagentastana.git
git push -u origin main
```

## Ubuntu: Быстрая установка
```bash
# 1. Системные пакеты (5 мин)
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib python3-dev libpq-dev

# 2. Клонирование проекта (1 мин)
cd ~
git clone https://github.com/YOUR_USERNAME/proagentastana.git
cd proagentastana

# 3. Python окружение (3 мин)
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Создание .env файла (2 мин)
nano .env
# Скопируйте содержимое из инструкции

# 5. База данных (3 мин)
sudo -u postgres createdb proagentastana_db
sudo -u postgres createuser -s proagentastana_user
sudo -u postgres psql -c "ALTER USER proagentastana_user PASSWORD 'your_password';"

# 6. Django настройка (3 мин)
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 7. Импорт данных (2 мин)
python manage.py import_reference_data --input reference_data.json
python manage.py import_housing_complexes --file housing_complexes_v2_utf8.csv

# 8. Запуск (1 мин)
python manage.py runserver 0.0.0.0:8000
```

## .env файл для Ubuntu
```env
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Для Neon DB (рекомендуется)
DATABASE_URL=postgresql://username:password@ep-host.neon.tech/dbname?sslmode=require

# Или локальная PostgreSQL
DB_NAME=proagentastana_db
DB_USER=proagentastana_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

MEDIA_ROOT=/home/username/proagentastana/media
STATIC_ROOT=/home/username/proagentastana/staticfiles
```

## Проверка работы
```bash
# После запуска откройте в браузере:
http://your-server-ip:8000

# Или если на локальной машине:
http://localhost:8000

# Админка:
http://your-server-ip:8000/admin/
```

## Troubleshooting
```bash
# Если ошибки с зависимостями:
sudo apt install -y python3-dev libpq-dev build-essential
pip install psycopg2-binary

# Если ошибки с правами на файлы:
sudo chown -R $USER:$USER ~/proagentastana
chmod +x manage.py

# Если ошибки с портами:
sudo ufw allow 8000
sudo ufw allow 80
sudo ufw allow 443

# Проверка логов:
python manage.py check
python manage.py showmigrations
```

## Что должно работать после установки:
✅ Главная страница со списком объявлений  
✅ Регистрация и авторизация  
✅ Создание объявлений  
✅ Загрузка фотографий  
✅ Админ панель (/admin/)  
✅ 1249 жилых комплексов в базе  
✅ Справочники (микрорайоны, типы ремонта и т.д.)  

**Общее время установки: ~20 минут** 
# 🚀 Руководство по развертыванию ProAgentAstana на PythonAnywhere

## 📋 Обзор

Это подробное руководство поможет вам развернуть ваш Django проект ProAgentAstana на платформе PythonAnywhere. Мы пройдем через все этапы от регистрации до запуска сайта.

## 🎯 Что мы получим в итоге

- Работающий сайт на домене `proagentastana.kz` (ваш кастомный домен)
- Подключенную Neon PostgreSQL базу данных
- Настроенные статические файлы
- Безопасные настройки для продакшена

## ⚠️ Важное примечание

**Этот проект использует Neon PostgreSQL базу данных.** Убедитесь, что у вас есть:
- Активный аккаунт на [neon.tech](https://neon.tech)
- Созданная база данных в Neon
- Данные для подключения (connection string)
- **Кастомный домен:** proagentastana.kz (уже куплен на hoster.kz)

---

## 📝 Шаг 1: Регистрация на PythonAnywhere

### 1.1 Создание аккаунта
1. Перейдите на [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Нажмите "Create a Beginner account" (бесплатный план)
3. Заполните форму регистрации:
   - Username: выберите уникальное имя пользователя
   - Email: ваш email
   - Password: надежный пароль
4. Подтвердите email

### 1.2 Активация аккаунта
1. Проверьте почту и перейдите по ссылке активации
2. Войдите в свой аккаунт PythonAnywhere

---

## 🖥️ Шаг 2: Подготовка проекта

### 2.1 Создание .gitignore (если его нет)
Перед загрузкой на сервер создайте файл `.gitignore` в корне проекта:

```bash
# Создайте файл .gitignore в корне проекта
.env
*.sqlite3
/media/
/staticfiles/
__pycache__/
*.pyc
.DS_Store
```

### 2.2 Подготовка requirements.txt
Убедитесь, что ваш `requirements.txt` содержит все зависимости:

```txt
Django==5.2.3
psycopg2-binary==2.9.9
python-decouple==3.8
Pillow==10.4.0
gunicorn==21.2.0
whitenoise==6.6.0
```

### 2.3 Загрузка проекта в Git
1. Инициализируйте Git репозиторий (если еще не сделано):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Создайте репозиторий на GitHub:
   - Перейдите на [github.com](https://github.com)
   - Создайте новый репозиторий
   - Следуйте инструкциям для загрузки кода

---

## 🔧 Шаг 3: Настройка PythonAnywhere

### 3.1 Вход в Dashboard
1. Войдите в свой аккаунт PythonAnywhere
2. Вы попадете на Dashboard

### 3.2 Создание Web App
1. В Dashboard найдите раздел "Web"
2. Нажмите "Add a new web app"
3. Выберите домен: `yourusername.pythonanywhere.com` (временно)
4. Выберите "Manual configuration"
5. Выберите Python версию: **Python 3.11** (или последнюю доступную)

### 3.3 Настройка кастомного домена
**Важно:** Для использования кастомного домена нужен **Paid план** PythonAnywhere.

1. **Обновите план до Paid** (если еще не сделано):
   - В Dashboard перейдите в "Account"
   - Выберите "Change plan"
   - Выберите "Hacker" или выше план

2. **Добавьте кастомный домен:**
   - В разделе "Web" найдите ваше приложение
   - Перейдите на вкладку "Domains"
   - Добавьте домен: `proagentastana.kz`
   - Добавьте также: `www.proagentastana.kz`

3. **Настройте DNS записи** (в hoster.kz):
   - **A запись:** `proagentastana.kz` → `35.197.78.74`
   - **A запись:** `www.proagentastana.kz` → `35.197.78.74`
   - **CNAME запись:** `www` → `proagentastana.kz`

#### Подробная инструкция по настройке DNS в hoster.kz:
1. Войдите в панель управления hoster.kz
2. Перейдите в раздел "Домены" → "Управление DNS"
3. Выберите домен `proagentastana.kz`
4. Добавьте записи:
   ```
   Тип: A
   Имя: @ (или оставьте пустым)
   Значение: 35.197.78.74
   TTL: 3600
   
   Тип: A
   Имя: www
   Значение: 35.197.78.74
   TTL: 3600
   
   Тип: CNAME
   Имя: www
   Значение: proagentastana.kz
   TTL: 3600
   ```
5. Сохраните изменения
6. **Важно:** DNS изменения могут занять до 24 часов

### 3.3 Настройка виртуального окружения
1. В разделе "Web" найдите ваше приложение
2. Перейдите на вкладку "Virtual environment"
3. Введите путь: `/home/yourusername/.virtualenvs/proagentastana`
4. Нажмите "Create"

---

## 📥 Шаг 4: Загрузка кода

### 4.1 Клонирование репозитория
1. Откройте "Consoles" в Dashboard
2. Выберите "Bash"
3. Выполните команды:

```bash
# Перейдите в домашнюю директорию
cd ~

# Клонируйте ваш репозиторий
git clone https://github.com/yourusername/proagentastana.git

# Перейдите в папку проекта
cd proagentastana
```

### 4.2 Активация виртуального окружения
```bash
# Активируйте виртуальное окружение
workon proagentastana

# Установите зависимости
pip install -r requirements.txt
```

---

## 🗄️ Шаг 5: Настройка базы данных (Neon PostgreSQL)

### 5.1 Подготовка Neon базы данных
Ваша база данных уже настроена в Neon. Убедитесь, что у вас есть:
- **Connection string** из Neon Dashboard
- **Database name** (обычно `proagentastana_db`)
- **Username** и **password**
- **Host** (например: `ep-summer-glitter-a2djk0r0-pooler.eu-central-1.aws.neon.tech`)

#### Как получить данные подключения из Neon:
1. Войдите в [Neon Console](https://console.neon.tech)
2. Выберите ваш проект
3. Перейдите в раздел "Connection Details"
4. Скопируйте данные:
   - **Host:** `ep-xxx-xxx-xxx-xxx-pooler.region.aws.neon.tech`
   - **Database:** `proagentastana_db`
   - **User:** `neondb_owner`
   - **Password:** (скопируйте из Neon)
   - **Port:** `5432`

### 5.2 Настройка переменных окружения
1. В консоли создайте файл `.env`:
```bash
cd ~/proagentastana
nano .env
```

2. Добавьте следующие строки (замените на ваши реальные данные из Neon):
```env
# Database settings for Neon PostgreSQL
DB_NAME=proagentastana_db
DB_USER=neondb_owner
DB_PASSWORD=npg_mWqyM3aIFvD6
DB_HOST=ep-summer-glitter-a2djk0r0-pooler.eu-central-1.aws.neon.tech
DB_PORT=5432
DB_SSLMODE=require

# Django settings
SECRET_KEY=your_new_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com,proagentastana.kz,www.proagentastana.kz
```

**Важно:** Замените данные на ваши реальные из Neon Dashboard!

3. Сохраните файл (Ctrl+X, затем Y, затем Enter)

### 5.3 Генерация нового SECRET_KEY
В консоли выполните:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Скопируйте результат и замените `your_new_secret_key_here` в файле `.env`

### 5.4 Проверка подключения к Neon
Проверьте, что подключение к базе данных работает:
```bash
# Активируйте виртуальное окружение
workon proagentastana

# Проверьте подключение
python manage.py check --database default
```

Если есть ошибки подключения, проверьте:
- Правильность данных в `.env`
- Активность Neon базы данных
- SSL настройки

---

## ⚙️ Шаг 6: Настройка Django

### 6.1 Применение миграций
```bash
# Убедитесь, что виртуальное окружение активировано
workon proagentastana

# Примените миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Заполните тестовыми данными
python manage.py populate_sample_data
```

### 6.2 Сбор статических файлов
```bash
# Соберите статические файлы
python manage.py collectstatic --noinput
```

---

## 🌐 Шаг 7: Настройка Web App

### 7.1 Настройка WSGI файла
1. В Dashboard перейдите в раздел "Web"
2. Нажмите на ссылку WSGI configuration file
3. Замените содержимое файла на:

```python
import os
import sys

# Добавьте путь к проекту
path = '/home/yourusername/proagentastana'
if path not in sys.path:
    sys.path.append(path)

# Настройка переменных окружения
os.environ['DJANGO_SETTINGS_MODULE'] = 'proagentastana.settings'

# Импорт Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. Сохраните файл

### 7.2 Настройка статических файлов
1. В разделе "Web" найдите "Static files"
2. Добавьте следующие записи:
   - URL: `/static/`
   - Directory: `/home/yourusername/proagentastana/staticfiles`
   - URL: `/media/`
   - Directory: `/home/yourusername/proagentastana/media`

### 7.3 Настройка доменов
1. В разделе "Web" найдите "Code"
2. В поле "Source code" укажите: `/home/yourusername/proagentastana`
3. В поле "Working directory" укажите: `/home/yourusername/proagentastana`

---

## 🔒 Шаг 8: Настройка безопасности

### 8.1 Обновление settings.py
В файле `proagentastana/settings.py` убедитесь, что:

```python
# Безопасность для продакшена
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Настройки безопасности
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 8.2 Настройка HTTPS (опционально)
Если у вас есть SSL сертификат:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 🚀 Шаг 9: Запуск сайта

### 9.1 Перезапуск Web App
1. В Dashboard перейдите в раздел "Web"
2. Нажмите зеленую кнопку "Reload yourusername.pythonanywhere.com"

### 9.2 Проверка работы
1. Откройте браузер
2. Проверьте сайт по адресам:
   - `https://yourusername.pythonanywhere.com` (временно)
   - `https://proagentastana.kz` (после настройки DNS)
   - `https://www.proagentastana.kz` (после настройки DNS)
3. Проверьте, что сайт загружается

### 9.3 Проверка админки
1. Перейдите по адресу: `https://proagentastana.kz/admin/`
2. Войдите с созданными учетными данными

### 9.4 Проверка DNS
После настройки DNS записей проверьте:
```bash
# Проверка A записи
nslookup proagentastana.kz

# Проверка www поддомена
nslookup www.proagentastana.kz
```

---

## 🔧 Шаг 10: Отладка и мониторинг

### 10.1 Просмотр логов
1. В Dashboard перейдите в раздел "Web"
2. Нажмите на "Log files"
3. Проверьте:
   - Error log
   - Server log
   - Access log

### 10.2 Частые проблемы и решения

#### Проблема: "ModuleNotFoundError"
**Решение:**
```bash
# Активируйте виртуальное окружение
workon proagentastana

# Переустановите зависимости
pip install -r requirements.txt
```

#### Проблема: "Database connection failed"
**Решение:**
1. Проверьте настройки в `.env` (особенно данные из Neon)
2. Убедитесь, что Neon база данных активна
3. Проверьте SSL настройки (DB_SSLMODE=require)
4. Убедитесь, что IP адрес PythonAnywhere разрешен в Neon
5. Проверьте connection string в Neon Dashboard

#### Проблема: "Static files not found"
**Решение:**
```bash
# Пересоберите статические файлы
python manage.py collectstatic --noinput

# Перезапустите Web App
```

#### Проблема: "Domain not working"
**Решение:**
1. Убедитесь, что у вас Paid план PythonAnywhere
2. Проверьте DNS записи в hoster.kz
3. Подождите до 24 часов для распространения DNS
4. Проверьте настройки в PythonAnywhere → Web → Domains
5. Убедитесь, что домен добавлен в ALLOWED_HOSTS

#### Проблема: "SSL certificate not working"
**Решение:**
1. PythonAnywhere автоматически предоставляет SSL для кастомных доменов
2. Подождите до 24 часов после добавления домена
3. Проверьте, что DNS записи настроены правильно

---

## 📊 Шаг 11: Мониторинг и обслуживание

### 11.1 Регулярные задачи
1. **Ежедневно:**
   - Проверяйте логи на ошибки
   - Мониторьте использование ресурсов

2. **Еженедельно:**
   - Обновляйте зависимости: `pip install --upgrade -r requirements.txt`
   - Проверяйте резервные копии

3. **Ежемесячно:**
   - Обновляйте Django до последней версии
   - Проверяйте безопасность

### 11.2 Резервное копирование
```bash
# Экспорт базы данных
python manage.py dumpdata > backup.json

# Резервное копирование медиа файлов
tar -czf media_backup.tar.gz media/
```

---

## 🎉 Поздравляем!

Ваш сайт ProAgentAstana успешно развернут на PythonAnywhere!

### 🔗 Полезные ссылки
- **Ваш сайт:** `https://proagentastana.kz`
- **Админка:** `https://proagentastana.kz/admin/`
- **PythonAnywhere Dashboard:** [www.pythonanywhere.com/user/yourusername](https://www.pythonanywhere.com/user/yourusername)
- **Hoster.kz DNS управление:** [панель управления hoster.kz](https://hoster.kz)

### 📞 Поддержка
- **PythonAnywhere Support:** [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Django Documentation:** [docs.djangoproject.com](https://docs.djangoproject.com)

---

## 🔄 Обновление сайта

Когда вы внесете изменения в код:

1. **Загрузите изменения в Git:**
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```

2. **Обновите код на сервере:**
   ```bash
   cd ~/proagentastana
   git pull
   ```

3. **Примените миграции (если есть):**
   ```bash
   workon proagentastana
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. **Перезапустите Web App:**
   - В Dashboard → Web → Reload

---

**Удачи с вашим проектом! 🚀** 
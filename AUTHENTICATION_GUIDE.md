# Руководство по системе аутентификации ProAgentAstana

## Обзор

Система аутентификации ProAgentAstana создана для обеспечения безопасного доступа к платформе недвижимости только для зарегистрированных пользователей-риэлторов.

## Ключевые особенности

1. **Авторизация по телефону** - вместо email используется номер телефона
2. **Обязательная авторизация** - доступ только для зарегистрированных пользователей
3. **Персонализированные приветствия** - различные сообщения для новых и существующих пользователей
4. **Система агентств** - каждый пользователь привязан к агентству недвижимости
5. **Автодополнение агентств** - умный поиск существующих агентств при регистрации

## Компоненты системы

### 1. Middleware для обязательной авторизации

**Файл:** `main/middleware.py`

```python
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверка авторизации для всех страниц кроме исключений
        if not request.user.is_authenticated:
            if not self.is_excluded_path(request.path):
                return HttpResponseRedirect('/login/')
        
        return self.get_response(request)
```

### 2. Кастомная модель пользователя

**Файл:** `main/models.py`

- Использует телефон как USERNAME_FIELD
- Связь с агентством через ForeignKey
- Поле `is_first_login` для отслеживания первого входа

### 3. Формы авторизации

**Файлы:** `main/forms.py`

- `PhoneLoginForm` - форма входа по телефону
- `UserRegistrationForm` - форма регистрации с автодополнением агентства

### 4. Views для авторизации

**Файл:** `main/views.py`

- `CustomLoginView` - обработка входа
- `UserRegistrationView` - обработка регистрации
- `agency_autocomplete` - AJAX эндпоинт для автодополнения

### 5. Автодополнение агентств

**Новая функциональность:**

#### AJAX Эндпоинт
```python
def agency_autocomplete(request):
    """AJAX endpoint for agency autocomplete"""
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if len(query) >= 1:
            agencies = Agency.objects.filter(name__icontains=query)[:10]
            # Возвращает JSON с предложениями агентств
```

#### Фронтенд функции
- **Поиск в реальном времени** - начинается с первого символа
- **Debounce** - задержка 300ms для оптимизации запросов
- **Навигация клавиатурой** - стрелки вверх/вниз, Enter, Escape
- **Показ статистики** - количество агентов в каждом агентстве

#### Как это работает:

1. **Ввод текста** - пользователь печатает название агентства
2. **AJAX запрос** - через 300ms отправляется запрос на сервер
3. **Поиск** - сервер ищет совпадения в названиях агентств
4. **Отображение** - показывается список подходящих агентств
5. **Выбор** - пользователь выбирает существующее или продолжает ввод нового

#### Создание нового агентства:

Если пользователь вводит название агентства, которого нет в базе, оно автоматически создается:

```python
# В UserRegistrationView
agency, agency_created = Agency.objects.get_or_create(name=agency_name)
```

## Настройка

### 1. Подключение middleware

**Файл:** `proagentastana/settings.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'main.middleware.LoginRequiredMiddleware',  # Наше middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 2. Настройка пользовательской модели

```python
AUTH_USER_MODEL = 'main.User'
```

### 3. URL-ы для автодополнения

**Файл:** `main/urls.py`

```python
urlpatterns = [
    # ... другие URL-ы
    path('ajax/agency-autocomplete/', views.agency_autocomplete, name='agency_autocomplete'),
]
```

## Тестирование автодополнения

### Существующие агентства в базе:
- Astana Real Estate
- Capital Properties  
- Elite Realty Astana
- Premier Properties

### Сценарии тестирования:

1. **Поиск существующего агентства:**
   - Введите "Astana" → должно показать "Astana Real Estate"
   - Введите "Capital" → должно показать "Capital Properties"

2. **Создание нового агентства:**
   - Введите "Новое Агентство" → должно создать новое агентство при регистрации

3. **Навигация клавиатурой:**
   - Введите "a" → используйте стрелки для навигации
   - Нажмите Enter для выбора

## Безопасность

1. **Телефонная авторизация** - проверка формата телефона
2. **Обязательная авторизация** - middleware блокирует неавторизованный доступ
3. **CSRF защита** - встроенная защита Django
4. **Валидация данных** - проверка всех полей форм

## Пользовательский опыт

### Персонализированные сообщения:

1. **Первый вход:**
   ```
   Добро пожаловать в ProAgentAstana, [Имя]! Это ваш первый вход в систему.
   Начните с добавления своего первого объявления о недвижимости!
   ```

2. **Повторный вход:**
   ```
   С возвращением, [Имя]!
   ```

3. **Новое агентство:**
   ```
   Registration successful! Welcome to ProAgentAstana! 
   New agency "[Название]" has been created.
   ```

### Автодополнение агентств:

- **Интуитивный поиск** - пользователь видит существующие агентства
- **Быстрый выбор** - клик или Enter для выбора
- **Статистика** - количество агентов в каждом агентстве
- **Создание нового** - если агентства нет, оно создается автоматически

## Обработка ошибок

1. **Валидация телефона** - проверка формата 7(XXX)-XXX-XXXX
2. **Уникальность телефона** - проверка существования пользователя
3. **Обработка AJAX ошибок** - graceful degradation при проблемах с сетью
4. **Логирование** - все ошибки регистрации логируются

## Файловая структура

```
main/
├── middleware.py          # LoginRequiredMiddleware
├── models.py             # User, Agency модели
├── forms.py              # Формы авторизации
├── views.py              # Views + agency_autocomplete
├── urls.py               # URL patterns
└── migrations/
    └── 0006_add_first_login_field.py

templates/main/
├── login.html            # Форма входа
└── user_register.html    # Форма регистрации с автодополнением
```

## Будущие улучшения

1. **Двухфакторная авторизация** - SMS коды
2. **Социальная авторизация** - вход через соцсети
3. **Расширенная система ролей** - админы агентств
4. **Аналитика входов** - статистика авторизаций
5. **Геопозиция агентств** - привязка к местоположению

---

*Система создана для обеспечения профессиональной платформы риэлторов с удобной авторизацией и умным поиском агентств.* 
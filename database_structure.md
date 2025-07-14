# Структура базы данных ProAgentAstana

## Информация о подключении
- **База данных**: proagentastana_db
- **Пользователь**: proagentastana_user
- **Хост**: 127.0.0.1
- **Порт**: 5433

## Статистика
- **Всего таблиц**: 22
- **Статус подключения**: ✅ Успешно

---

## Таблицы приложения

### 1. addresses (Адреса)
**Назначение**: Хранение адресной информации объектов недвижимости

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('addresses_id_seq') |
| microdistrict | character varying | NULL | |
| complex_name | character varying | NULL | |
| street | character varying | NULL | |
| building_no | character varying | NULL | |
| latitude | numeric | NULL | |
| longitude | numeric | NULL | |

**Количество записей**: 2

### 2. agencies (Агентства)
**Назначение**: Информация о агентствах недвижимости

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('agencies_id_seq') |
| name | character varying | NOT NULL | |
| created_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |

**Количество записей**: 4

### 3. announcements (Объявления)
**Назначение**: Объявления о продаже/аренде недвижимости

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('announcements_id_seq') |
| user_id | integer | NOT NULL, FK | |
| address_id | integer | NOT NULL, FK | |
| rooms_count | smallint | NOT NULL | |
| price | bigint | NOT NULL | |
| repair_status | USER-DEFINED | NOT NULL | |
| building_type | character varying | NULL | |
| year_built | integer | NULL | |
| is_new_building | boolean | NULL | false |
| floor | smallint | NULL | |
| total_floors | smallint | NULL | |
| area | numeric | NOT NULL | |
| description | text | NULL | |
| is_archived | boolean | NULL | false |
| created_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |

**Количество записей**: 0

### 4. collections (Коллекции)
**Назначение**: Пользовательские коллекции избранных объявлений

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('collections_id_seq') |
| user_id | integer | NOT NULL, FK | |
| name | character varying | NOT NULL | |
| created_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |

**Количество записей**: 0

### 5. collection_items (Элементы коллекций)
**Назначение**: Связь между коллекциями и объявлениями

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('collection_items_id_seq') |
| collection_id | integer | NOT NULL, FK | |
| announcement_id | integer | NOT NULL, FK | |
| added_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |

**Количество записей**: 0

### 6. photos (Фотографии объявлений)
**Назначение**: Фотографии к объявлениям

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('photos_id_seq') |
| announcement_id | integer | NOT NULL, FK | |
| is_main | boolean | NULL | false |
| uploaded_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |
| file_name | character varying | NOT NULL | |
| file_path | character varying | NOT NULL | |
| file_size | integer | NULL | |
| mime_type | character varying | NULL | |
| original_name | character varying | NULL | |

**Количество записей**: 0

### 7. users (Пользователи)
**Назначение**: Основная таблица пользователей системы

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('users_id_seq') |
| phone | character varying | NOT NULL, UNIQUE | |
| password_hash | character varying | NOT NULL | |
| agency_id | integer | NULL, FK | |
| is_active | boolean | NOT NULL | true |
| created_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |
| additional_phone | character varying | NULL | |
| email | character varying | NULL | |
| first_name | character varying | NOT NULL | |
| last_name | character varying | NOT NULL | |
| whatsapp_phone | character varying | NULL | |
| last_login | timestamp with time zone | NULL | |

**Количество записей**: 1

### 8. user_photos (Фотографии пользователей)
**Назначение**: Фотографии профилей пользователей

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | bigint | NOT NULL, PK | |
| file_name | character varying | NOT NULL | |
| file_path | character varying | NOT NULL | |
| file_size | integer | NULL | |
| mime_type | character varying | NULL | |
| original_name | character varying | NULL | |
| is_main | boolean | NOT NULL | |
| uploaded_at | timestamp with time zone | NOT NULL | |
| user_id | bigint | NOT NULL, FK | |

**Количество записей**: 0

### 9. tariffs (Тарифы)
**Назначение**: Тарифные планы для пользователей

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('tariffs_id_seq') |
| name | character varying | NOT NULL | |
| price | numeric | NOT NULL | |
| duration_days | integer | NOT NULL | |
| created_at | timestamp without time zone | NULL | CURRENT_TIMESTAMP |

**Количество записей**: 2

### 10. subscriptions (Подписки)
**Назначение**: Подписки пользователей на тарифы

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('subscriptions_id_seq') |
| user_id | integer | NOT NULL, FK | |
| tariff_id | integer | NOT NULL, FK | |
| start_date | date | NOT NULL | |
| end_date | date | NOT NULL | |
| active | boolean | NULL | true |

**Количество записей**: 0

### 11. page_views (Просмотры страниц)
**Назначение**: Статистика просмотров страниц

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('page_views_id_seq') |
| user_id | integer | NOT NULL, FK | |
| path | character varying | NOT NULL | |
| timestamp | timestamp without time zone | NULL | CURRENT_TIMESTAMP |
| duration_seconds | integer | NULL | |

**Количество записей**: 0

### 12. user_sessions (Пользовательские сессии)
**Назначение**: Отслеживание сессий пользователей

| Колонка | Тип | Ограничения | По умолчанию |
|---------|-----|-------------|--------------|
| id | integer | NOT NULL, PK | nextval('user_sessions_id_seq') |
| user_id | integer | NOT NULL, FK | |
| session_key | character varying | NOT NULL | |
| login_time | timestamp without time zone | NOT NULL | |
| logout_time | timestamp without time zone | NULL | |
| duration | interval | NULL | |

**Количество записей**: 0

---

## Системные таблицы Django

### Django Authentication
- **auth_group**: 0 записей
- **auth_group_permissions**: 0 записей
- **auth_permission**: 72 записи
- **auth_user**: 0 записей
- **auth_user_groups**: 0 записей
- **auth_user_user_permissions**: 0 записей

### Django System
- **django_admin_log**: 0 записей
- **django_content_type**: 18 записей
- **django_migrations**: 21 запись
- **django_session**: 4 записи

---

## Анализ данных

### Состояние базы данных
- ✅ База данных подключена и работает
- 📊 Структура таблиц создана корректно
- 🏢 Есть данные об агентствах (4 записи)
- 📍 Есть адресные данные (2 записи)  
- 💰 Настроены тарифы (2 записи)
- 👤 Есть один пользователь в системе
- 📄 Объявления отсутствуют (0 записей)

### Рекомендации
1. Заполнить тестовые объявления
2. Создать дополнительных пользователей для тестирования
3. Добавить фотографии к объявлениям
4. Проверить работу системы коллекций

---

*Дата создания отчета: Автоматически сгенерирован при подключении к БД* 
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from decimal import Decimal


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""
    
    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular user with the given phone and password."""
        if not phone:
            raise ValueError('The Phone field must be set')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and save a superuser with the given phone and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_fields)


class Agency(models.Model):
    """Real Estate Agency model"""
    name = models.CharField(max_length=255, verbose_name="Agency Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"
        db_table = "agencies"

    def __str__(self):
        return self.name


# Новые модели справочников
class Microdistrict(models.Model):
    """Microdistrict (районы города) справочник"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    name = models.CharField(max_length=255, verbose_name="Название")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Микрорайон"
        verbose_name_plural = "Микрорайоны"
        db_table = "microdistricts"
        ordering = ['name']

    def __str__(self):
        return self.name


class RepairType(models.Model):
    """Repair Type (виды ремонта) справочник"""
    name = models.CharField(max_length=255, verbose_name="Название")
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Тип ремонта"
        verbose_name_plural = "Типы ремонта"
        db_table = "repair_types"
        ordering = ['name']

    def __str__(self):
        return self.name


class BuildingType(models.Model):
    """Building Type (типы домов) справочник"""
    name = models.CharField(max_length=255, verbose_name="Название")
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Тип дома"
        verbose_name_plural = "Типы домов"
        db_table = "building_types"
        ordering = ['name']

    def __str__(self):
        return self.name


class ResidentialComplex(models.Model):
    """Residential Complex (ЖК) справочник"""
    name = models.CharField(max_length=255, verbose_name="Название ЖК")
    microdistrict = models.ForeignKey(
        Microdistrict, 
        on_delete=models.CASCADE, 
        related_name='complexes',
        verbose_name="Микрорайон"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Жилой комплекс"
        verbose_name_plural = "Жилые комплексы"
        db_table = "residential_complexes"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.microdistrict.name})"


class User(AbstractUser):
    """Custom User model for real estate agents"""
    username = None  # Remove username field
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        unique=True, 
        verbose_name="Phone Number"
    )
    additional_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True, 
        verbose_name="Additional Phone"
    )
    whatsapp_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True, 
        verbose_name="WhatsApp Phone"
    )
    
    agency = models.ForeignKey(
        Agency, 
        on_delete=models.CASCADE, 
        related_name='users',
        verbose_name="Agency"
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_first_login = models.BooleanField(default=True, verbose_name="Is First Login")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'agency']
    
    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"


class UserPhoto(models.Model):
    """User photos model"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='photos',
        verbose_name="User"
    )
    file_name = models.CharField(max_length=255, verbose_name="File Name")
    file_path = models.CharField(max_length=500, verbose_name="File Path")
    file_size = models.BigIntegerField(verbose_name="File Size")
    mime_type = models.CharField(max_length=100, verbose_name="MIME Type")
    original_name = models.CharField(max_length=255, verbose_name="Original Name")
    is_main = models.BooleanField(default=False, verbose_name="Is Main Photo")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")

    class Meta:
        verbose_name = "User Photo"
        verbose_name_plural = "User Photos"
        db_table = "user_photos"

    def __str__(self):
        return f"{self.user.first_name}'s photo - {self.file_name}"


class Address(models.Model):
    """Property address model"""
    microdistrict = models.CharField(max_length=255, blank=True, null=True, verbose_name="Microdistrict")
    complex_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complex Name")
    street = models.CharField(max_length=255, blank=True, null=True, verbose_name="Street")
    building_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="Building Number")
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        blank=True, 
        null=True, 
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        blank=True, 
        null=True, 
        verbose_name="Longitude"
    )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        db_table = "addresses"

    def __str__(self):
        parts = [self.microdistrict, self.complex_name, self.street, self.building_no]
        return ", ".join([part for part in parts if part])


class Landmark(models.Model):
    """Landmark model for property locations"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    name = models.CharField(max_length=255, verbose_name="Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Landmark"
        verbose_name_plural = "Landmarks"
        db_table = "landmarks"
        ordering = ['name']

    def __str__(self):
        return self.name


class Announcement(models.Model):
    """Property listing model"""
    REPAIR_STATUS_CHOICES = [
        ('Черновая отделка', 'Черновая отделка'),
        ('Новый ремонт', 'Новый ремонт'),
        ('Не новый, но аккуратный ремонт', 'Не новый, но аккуратный ремонт'),
        ('Старый ремонт', 'Старый ремонт'),
    ]

    COMMISSION_TYPE_CHOICES = [
        ('seller', 'Я беру с продавца, вы берете с покупателя'),
        ('split', 'Я беру с продавца и (ввод числа) тенге с покупателя. Остальное ваше'),
        ('buyer', 'Я беру с продавца, вы - с покупателя и я дополнительно доплачиваю вам (ввод числа) тенге'),
    ]

    LANDMARK_CHOICES = [
        ('', 'Не выбрано'),
        ('central_mosque', 'Центральная (Новая) Мечеть'),
        ('expo_mega', 'ЭКСПО и ТРЦ "MEGA Silkway"'),
        ('nazarbayev_university', 'Назарбаев Университет'),
        ('ellington_mall', 'ТРК "Эллингтон Молл"'),
        ('barys_astana_arena', 'Барыс Арена и Астана Арена'),
        ('botanical_garden', 'Ботанический сад'),
        ('sphere_park', 'Сфера Парк'),
        ('presidential_park_left', 'Президентский парк (Левый берег)'),
        ('presidential_park_right', 'Президентский парк (Правый берег)'),
        ('khan_shatyr', 'Хан Шатыр'),
        ('abu_dhabi_baiterek', 'Абу Даби Плаза и Байтерек'),
        ('central_park', 'Центральный парк'),
        ('pyramid', 'Пирамида'),
        ('new_station', 'Новый вокзал'),
        ('triathlon_park', 'Триатлон Парк'),
        ('meeting_center', 'ТЦ "Встреча"'),
        ('eurasia_mall', 'ТРЦ "Евразия"'),
        ('akimat_museum', 'Здание акимата (Музей первого Президента)'),
        ('koktal_park', 'Парк "Коктал"'),
        ('artem_market', 'Рынок Артём'),
        ('old_station', 'Старый вокзал'),
        ('central_embankment', 'Центральная набережная'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='announcements',
        verbose_name="User"
    )
    address = models.ForeignKey(
        Address, 
        on_delete=models.CASCADE, 
        related_name='announcements',
        verbose_name="Address"
    )
    rooms_count = models.SmallIntegerField(verbose_name="Number of Rooms")
    price = models.BigIntegerField(verbose_name="Price")
    repair_status = models.CharField(
        max_length=35, 
        choices=REPAIR_STATUS_CHOICES, 
        verbose_name="Repair Status"
    )
    building_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Building Type")
    year_built = models.IntegerField(blank=True, null=True, verbose_name="Year Built")
    is_new_building = models.BooleanField(default=False, verbose_name="Is New Building")
    floor = models.SmallIntegerField(blank=True, null=True, verbose_name="Floor")
    total_floors = models.SmallIntegerField(blank=True, null=True, verbose_name="Total Floors")
    area = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Area (sq.m)")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Опорные точки (множественный выбор)
    landmarks = models.ManyToManyField(
        Landmark, 
        blank=True, 
        related_name='announcements',
        verbose_name="Landmarks"
    )
    
    # Новые поля
    krisha_link = models.URLField(blank=True, null=True, verbose_name="Krisha.kz Link")
    commission_type = models.CharField(
        max_length=20, 
        choices=COMMISSION_TYPE_CHOICES, 
        verbose_name="Commission Type"
    )
    commission_percentage = models.IntegerField(blank=True, null=True, verbose_name="Commission Percentage")
    commission_amount = models.IntegerField(blank=True, null=True, verbose_name="Commission Amount")
    commission_bonus = models.IntegerField(blank=True, null=True, verbose_name="Commission Bonus")
    
    is_archived = models.BooleanField(default=False, verbose_name="Is Archived")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        db_table = "announcements"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rooms_count}-room apartment - {self.price}"


class Photo(models.Model):
    """Listing photos model"""
    announcement = models.ForeignKey(
        Announcement, 
        on_delete=models.CASCADE, 
        related_name='photos',
        verbose_name="Announcement"
    )
    file_name = models.CharField(max_length=255, verbose_name="File Name")
    file_path = models.CharField(max_length=500, verbose_name="File Path")
    file_size = models.BigIntegerField(verbose_name="File Size")
    mime_type = models.CharField(max_length=100, verbose_name="MIME Type")
    original_name = models.CharField(max_length=255, verbose_name="Original Name")
    is_main = models.BooleanField(default=False, verbose_name="Is Main Photo")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")
    
    # Thumbnail fields
    thumbnail_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Thumbnail Path")
    thumbnail_size = models.BigIntegerField(blank=True, null=True, verbose_name="Thumbnail Size")

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        db_table = "photos"

    def __str__(self):
        return f"Photo for {self.announcement} - {self.file_name}"


class Collection(models.Model):
    """Collection of listings model"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='collections',
        verbose_name="User"
    )
    name = models.CharField(max_length=255, verbose_name="Collection Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
        db_table = "collections"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.user.first_name}"


class CollectionItem(models.Model):
    """Collection items model"""
    collection = models.ForeignKey(
        Collection, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Collection"
    )
    announcement = models.ForeignKey(
        Announcement, 
        on_delete=models.CASCADE, 
        related_name='collection_items',
        verbose_name="Announcement"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Added At")

    class Meta:
        verbose_name = "Collection Item"
        verbose_name_plural = "Collection Items"
        db_table = "collection_items"
        unique_together = ['collection', 'announcement']

    def __str__(self):
        return f"{self.announcement} in {self.collection.name}"


class Tariff(models.Model):
    """Tariff model for future expansion"""
    name = models.CharField(max_length=255, verbose_name="Tariff Name")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    duration_days = models.IntegerField(verbose_name="Duration (days)")
    features = models.TextField(verbose_name="Features")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Tariff"
        verbose_name_plural = "Tariffs"
        db_table = "tariffs"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Subscription model for future expansion"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name="User"
    )
    tariff = models.ForeignKey(
        Tariff, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name="Tariff"
    )
    start_date = models.DateTimeField(verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        db_table = "subscriptions"

    def __str__(self):
        return f"{self.user} - {self.tariff}"


class UserSession(models.Model):
    """User sessions model"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        verbose_name="User"
    )
    session_key = models.CharField(max_length=40, verbose_name="Session Key")
    login_time = models.DateTimeField(verbose_name="Login Time")
    logout_time = models.DateTimeField(blank=True, null=True, verbose_name="Logout Time")
    duration = models.DurationField(blank=True, null=True, verbose_name="Duration")

    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        db_table = "user_sessions"

    def __str__(self):
        return f"{self.user} - {self.login_time}"


class PageView(models.Model):
    """Page views model"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='page_views',
        verbose_name="User"
    )
    path = models.CharField(max_length=500, verbose_name="Page Path")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    duration_seconds = models.IntegerField(default=0, verbose_name="Duration (seconds)")

    class Meta:
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        db_table = "page_views"

    def __str__(self):
        return f"{self.user} viewed {self.path}"


class UserActivity(models.Model):
    """Detailed user activity tracking model"""
    
    ACTION_TYPES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('view_page', 'Просмотр страницы'),
        ('create_announcement', 'Создание объявления'),
        ('edit_announcement', 'Редактирование объявления'),
        ('delete_announcement', 'Удаление объявления'),
        ('archive_announcement', 'Архивирование объявления'),
        ('unarchive_announcement', 'Восстановление объявления'),
        ('auto_archive_announcement', 'Автоматическое архивирование объявления'),
        ('view_announcement', 'Просмотр объявления'),
        ('search_announcements', 'Поиск объявлений'),
        ('filter_announcements', 'Фильтрация объявлений'),
        ('create_collection', 'Создание коллекции'),
        ('edit_collection', 'Редактирование коллекции'),
        ('delete_collection', 'Удаление коллекции'),
        ('add_to_collection', 'Добавление в коллекцию'),
        ('remove_from_collection', 'Удаление из коллекции'),
        ('view_collection', 'Просмотр коллекции'),
        ('upload_photo', 'Загрузка фото'),
        ('delete_photo', 'Удаление фото'),
        ('set_main_photo', 'Установка главного фото'),
        ('upload_user_photo', 'Загрузка фото профиля'),
        ('update_profile', 'Обновление профиля'),
        ('view_profile', 'Просмотр профиля'),
        ('change_password', 'Изменение пароля'),
        ('export_data', 'Экспорт данных'),
        ('api_call', 'API запрос'),
        ('error', 'Ошибка'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activities',
        verbose_name="Пользователь"
    )
    action_type = models.CharField(
        max_length=50, 
        choices=ACTION_TYPES,
        verbose_name="Тип действия"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Описание"
    )
    
    # Дополнительные данные в JSON формате
    metadata = models.JSONField(
        blank=True, 
        null=True,
        verbose_name="Метаданные"
    )
    
    # IP адрес и User Agent
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name="IP адрес"
    )
    user_agent = models.TextField(
        blank=True, 
        null=True,
        verbose_name="User Agent"
    )
    
    # Ссылка на связанные объекты
    related_announcement = models.ForeignKey(
        'Announcement',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='activities',
        verbose_name="Связанное объявление"
    )
    related_collection = models.ForeignKey(
        'Collection',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='activities',
        verbose_name="Связанная коллекция"
    )
    
    # Время и сессия
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время")
    session_key = models.CharField(
        max_length=40, 
        blank=True, 
        null=True,
        verbose_name="Ключ сессии"
    )
    
    # Дополнительная информация о странице
    page_url = models.URLField(
        blank=True, 
        null=True,
        verbose_name="URL страницы"
    )
    referrer = models.URLField(
        blank=True, 
        null=True,
        verbose_name="Referrer"
    )
    
    # Статус успешности действия
    is_successful = models.BooleanField(
        default=True,
        verbose_name="Успешно"
    )
    error_message = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Сообщение об ошибке"
    )
    
    class Meta:
        verbose_name = "Активность пользователя"
        verbose_name_plural = "Активность пользователей"
        db_table = "user_activities"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_formatted_metadata(self):
        """Возвращает форматированные метаданные для отображения"""
        if not self.metadata:
            return "Нет данных"
        
        formatted = []
        for key, value in self.metadata.items():
            if key == 'search_params':
                formatted.append(f"Параметры поиска: {value}")
            elif key == 'filter_params':
                formatted.append(f"Фильтры: {value}")
            elif key == 'old_values':
                formatted.append(f"Старые значения: {value}")
            elif key == 'new_values':
                formatted.append(f"Новые значения: {value}")
            elif key == 'file_info':
                formatted.append(f"Файл: {value}")
            else:
                formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted)


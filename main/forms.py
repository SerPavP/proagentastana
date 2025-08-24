from django.core.cache import cache
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import User, Agency, Announcement, Collection, Address, Landmark


class PhoneLoginForm(AuthenticationForm):
    """Custom login form using phone number instead of username"""
    username = forms.CharField(
        label="Номер телефона",
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control phone-mask',
            'placeholder': '7(123)-123-1233',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            phone_digits = ''.join(filter(str.isdigit, username))
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                username = '+' + phone_digits
            else:
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(123)-123-1233")
        return username


class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        min_length=8
    )
    password_confirm = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    )
    
    # Изменяем поле агентства на текстовое
    agency_name = forms.CharField(
        label="Название агентства",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название вашего агентства'
        }),
        help_text="Введите название вашего агентства недвижимости"
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'additional_phone', 
            'whatsapp_phone', 'email'
        ]
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'phone': 'Номер телефона',
            'additional_phone': 'Дополнительный номер',
            'whatsapp_phone': 'WhatsApp номер',
            'email': 'Email'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '7(123)-123-1233'
            }),
            'additional_phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '7(123)-123-1233 (необязательно)'
            }),
            'whatsapp_phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '7(123)-123-1233 (необязательно)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email (необязательно)'
            })
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        
        return password_confirm

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Удаляем маску и оставляем только цифры, добавляем +
        if phone:
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                phone = '+' + phone_digits
            else:
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(123)-123-1233")
        
        return phone
    
    def clean_additional_phone(self):
        phone = self.cleaned_data.get('additional_phone')
        if phone:
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                phone = '+' + phone_digits
            else:
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(123)-123-1233")
        return phone
    
    def clean_whatsapp_phone(self):
        phone = self.cleaned_data.get('whatsapp_phone')
        if phone:
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                phone = '+' + phone_digits
            else:
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(123)-123-1233")
        return phone


class AnnouncementForm(forms.ModelForm):
    """Announcement creation/edit form"""
    
    # Address fields - using database models instead of hardcoded choices
    microdistrict = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=True,
        label="Микрорайон *",
        empty_label="Выберите микрорайон",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    complex_name = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label="Жилой комплекс",
        empty_label="Выберите жилой комплекс",
        widget=forms.Select(attrs={
            'class': 'form-select complex-autocomplete',
            'placeholder': 'Выберите жилой комплекс'
        })
    )
    
    street = forms.CharField(
        required=False,
        label="Улица",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название улицы'
        })
    )
    
    building_no = forms.CharField(
        required=False,
        label="Номер дома",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер дома'
        })
    )
    
    latitude = forms.DecimalField(
        required=False,
        label="Широта",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите широту',
            'step': 'any'
        })
    )
    longitude = forms.DecimalField(
        required=False,
        label="Долгота",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите долготу',
            'step': 'any'
        })
    )
    
    # Дополнительные поля для соответствия макету
    krisha_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://krisha.kz/...'
        }),
        label="Ссылка на объявление Krisha.kz"
    )
    
    COMMISSION_CHOICES = [
        ('seller', 'Я беру с продавца, вы берете с покупателя'),
        ('split', 'Я беру с продавца и (ввод числа) тенге с покупателя. Остальное ваше'),
        ('buyer', 'Я беру с продавца, вы - с покупателя и я дополнительно доплачиваю вам (ввод числа) тенге'),
    ]
    
    commission_type = forms.ChoiceField(
        choices=COMMISSION_CHOICES,
        required=True,
        widget=forms.RadioSelect(),
        label="Как я делюсь комиссией *"
    )
    
    commission_percentage = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'max': 100,
            'style': 'width: 80px; display: inline-block;'
        }),
        label="Процент с покупателя"
    )
    
    commission_amount = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'width: 150px; display: inline-block;',
            'placeholder': 'Введите сумму'
        }),
        label="Сумма тенге"
    )
    
    commission_bonus = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'width: 150px; display: inline-block;',
            'placeholder': 'Введите сумму'
        }),
        label="Доплата тенге"
    )

    # Using database models for repair status
    repair_status = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=True,
        label="Ремонт *",
        empty_label="Выберите состояние ремонта",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    # Using database models for building type
    building_type = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=True,
        label="Тип дома *",
        empty_label="Выберите тип дома",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    # Landmarks field - "Дом находится рядом с"
    landmarks = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label="Дом находится рядом с",
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Выберите достопримечательности рядом с домом"
    )

    class Meta:
        model = Announcement
        fields = [
            'rooms_count', 'price', 'area', 'floor', 'total_floors', 'year_built',
            'is_new_building', 'description', 'krisha_link', 'commission_type', 'commission_percentage', 
            'commission_amount', 'commission_bonus'
        ]
        
        widgets = {
            'rooms_count': forms.Select(choices=[(i, f"{i} комнаты" if i != 1 else "1 комната") for i in range(1, 6)], attrs={'class': 'form-select'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите цену в тенге'}),  # Изменили на TextInput для поддержки форматирования
            'area': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 1}),
            'floor': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'year_built': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2030}),
            'is_new_building': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите квартиру: особенности планировки, состояние, мебель, инфраструктура...'
            }),
        }
        
        labels = {
            'rooms_count': 'Количество комнат *',
            'price': 'Цена *',
            'area': 'Площадь (м²) *',
            'floor': 'Этаж *',
            'total_floors': 'Этажность дома *',
            'year_built': 'Год постройки *',
            'is_new_building': 'Новостройка',
            'description': 'Описание',  # Убираем звездочку - теперь не обязательное
        }

    def __init__(self, *args, **kwargs):
        # Import models here to avoid circular imports
        from .models import Microdistrict, RepairType, BuildingType, ResidentialComplex
        
        # Extract address data if editing existing announcement
        instance = kwargs.get('instance')
        if instance and instance.address:
            initial = kwargs.get('initial', {})
            
            # Handle microdistrict - find by name
            if instance.address.microdistrict:
                try:
                    microdistrict_obj = Microdistrict.objects.get(
                        name=instance.address.microdistrict, 
                        is_active=True
                    )
                    initial['microdistrict'] = microdistrict_obj
                except Microdistrict.DoesNotExist:
                    pass
            
            # Handle complex name - find by name
            if instance.address.complex_name:
                try:
                    complex_obj = ResidentialComplex.objects.get(
                        name=instance.address.complex_name, 
                        is_active=True
                    )
                    initial['complex_name'] = complex_obj
                except ResidentialComplex.DoesNotExist:
                    pass
            
            initial.update({
                'street': instance.address.street,
                'building_no': instance.address.building_no,
                'latitude': instance.address.latitude,
                'longitude': instance.address.longitude,
            })
            
            # Handle building_type - find by name
            if instance.building_type:
                try:
                    building_type_obj = BuildingType.objects.get(
                        name=instance.building_type, 
                        is_active=True
                    )
                    initial['building_type'] = building_type_obj
                except BuildingType.DoesNotExist:
                    pass
            
            # Handle repair_status - find by name
            if instance.repair_status:
                try:
                    repair_type_obj = RepairType.objects.get(
                        name=instance.repair_status, 
                        is_active=True
                    )
                    initial['repair_status'] = repair_type_obj
                except RepairType.DoesNotExist:
                    pass
            
            kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)
        
        # 🚀 Set cached querysets for model choice fields
        from django.core.cache import cache
        
        # Кэшированный queryset для микрорайонов
        microdistrict_qs_key = 'announcement_form_microdistrict_qs_v2'
        microdistrict_qs = cache.get(microdistrict_qs_key)
        if microdistrict_qs is None:
            microdistrict_qs = list(Microdistrict.objects.filter(is_active=True).order_by('name'))
            cache.set(microdistrict_qs_key, microdistrict_qs, 3600)  # 1 час
        self.fields['microdistrict'].queryset = Microdistrict.objects.filter(
            pk__in=[obj.pk for obj in microdistrict_qs]
        ).order_by('name')
        
        # Кэшированный queryset для ЖК: сначала русские названия (А-Я), потом английские (A-Z)
        complex_qs_key = 'announcement_form_complex_qs_v2'
        complex_qs = cache.get(complex_qs_key)
        if complex_qs is None:
            complex_qs = list(ResidentialComplex.objects.filter(is_active=True).extra(
                select={'name_sort': "CASE WHEN name ~ '^[А-Яа-я]' THEN '1' || name ELSE '2' || name END"}
            ).order_by('name_sort'))
            cache.set(complex_qs_key, complex_qs, 3600)
        self.fields['complex_name'].queryset = ResidentialComplex.objects.filter(
            pk__in=[obj.pk for obj in complex_qs]
        ).extra(
            select={'name_sort': "CASE WHEN name ~ '^[А-Яа-я]' THEN '1' || name ELSE '2' || name END"}
        ).order_by('name_sort')
        
        # Кэшированный queryset для типов ремонта
        repair_qs_key = 'announcement_form_repair_qs_v2'
        repair_qs = cache.get(repair_qs_key)
        if repair_qs is None:
            repair_qs = list(RepairType.objects.filter(is_active=True).order_by('name'))
            cache.set(repair_qs_key, repair_qs, 3600)
        self.fields['repair_status'].queryset = RepairType.objects.filter(
            pk__in=[obj.pk for obj in repair_qs]
        ).order_by('name')
        
        # Кэшированный queryset для типов домов: "иной" вверху, остальные по алфавиту
        building_type_qs_key = 'announcement_form_building_type_qs_v2'
        building_type_qs = cache.get(building_type_qs_key)
        if building_type_qs is None:
            building_type_qs = list(BuildingType.objects.filter(is_active=True).extra(
                select={'is_other': "CASE WHEN LOWER(name) = 'иной' THEN 0 ELSE 1 END"}
            ).order_by('is_other', 'name'))
            cache.set(building_type_qs_key, building_type_qs, 3600)
        self.fields['building_type'].queryset = BuildingType.objects.filter(
            pk__in=[obj.pk for obj in building_type_qs]
        ).extra(
            select={'is_other': "CASE WHEN LOWER(name) = 'иной' THEN 0 ELSE 1 END"}
        ).order_by('is_other', 'name')
        
        # Кэшированный queryset для landmarks
        landmarks_qs_key = 'announcement_form_landmarks_qs_v2'
        landmarks_qs = cache.get(landmarks_qs_key)
        if landmarks_qs is None:
            landmarks_qs = list(Landmark.objects.all().order_by('name'))
            cache.set(landmarks_qs_key, landmarks_qs, 3600)
        self.fields['landmarks'].queryset = Landmark.objects.filter(
            pk__in=[obj.pk for obj in landmarks_qs]
        ).order_by('name')

    def get_address_data(self):
        """Extract address data from cleaned form data"""
        microdistrict_obj = self.cleaned_data.get('microdistrict')
        complex_obj = self.cleaned_data.get('complex_name')
        
        return {
            'microdistrict': microdistrict_obj.name if microdistrict_obj else None,
            'complex_name': complex_obj.name if complex_obj else None,
            'street': self.cleaned_data.get('street'),
            'building_no': self.cleaned_data.get('building_no'),
            'latitude': self.cleaned_data.get('latitude'),
            'longitude': self.cleaned_data.get('longitude'),
        }
    
    def clean_price(self):
        """Валидация поля цены"""
        price = self.cleaned_data.get('price')
        if price:
            # Убираем форматирование (пробелы)
            price_str = str(price).replace(' ', '')
            try:
                price_value = int(price_str)
                if price_value < 0:
                    raise forms.ValidationError("Цена не может быть отрицательной")
                if price_value > 999999999999999:  # 15 цифр максимум
                    raise forms.ValidationError("Цена слишком большая")
                return price_value
            except ValueError:
                raise forms.ValidationError("Введите корректную цену")
        return price

    def clean_commission_amount(self):
        """Валидация поля суммы комиссии"""
        commission_amount = self.cleaned_data.get('commission_amount')
        if commission_amount:
            # Убираем форматирование (пробелы)
            commission_str = str(commission_amount).replace(' ', '')
            try:
                commission_value = int(commission_str)
                if commission_value < 0:
                    raise forms.ValidationError("Сумма комиссии не может быть отрицательной")
                if commission_value > 999999999999999:  # 15 цифр максимум
                    raise forms.ValidationError("Сумма комиссии слишком большая")
                return commission_value
            except ValueError:
                raise forms.ValidationError("Введите корректную сумму комиссии")
        return commission_amount

    def clean_commission_bonus(self):
        """Валидация поля доплаты комиссии"""
        commission_bonus = self.cleaned_data.get('commission_bonus')
        if commission_bonus:
            # Убираем форматирование (пробелы)
            commission_str = str(commission_bonus).replace(' ', '')
            try:
                commission_value = int(commission_str)
                if commission_value < 0:
                    raise forms.ValidationError("Доплата комиссии не может быть отрицательной")
                if commission_value > 999999999999999:  # 15 цифр максимум
                    raise forms.ValidationError("Доплата комиссии слишком большая")
                return commission_value
            except ValueError:
                raise forms.ValidationError("Введите корректную доплату комиссии")
        return commission_bonus

    def clean_repair_status(self):
        """Валидация поля ремонта"""
        repair_status = self.cleaned_data.get('repair_status')
        if repair_status and not repair_status.is_active:
            raise forms.ValidationError("Выберите активный тип ремонта")
        return repair_status

    def clean_building_type(self):
        """Валидация поля типа дома"""
        building_type = self.cleaned_data.get('building_type')
        if building_type and not building_type.is_active:
            raise forms.ValidationError("Выберите активный тип дома")
        return building_type

    def clean_microdistrict(self):
        """Валидация поля микрорайона"""
        microdistrict = self.cleaned_data.get('microdistrict')
        if microdistrict and not microdistrict.is_active:
            raise forms.ValidationError("Выберите активный микрорайон")
        return microdistrict

    def clean_krisha_link(self):
        """Валидация ссылки на Krisha.kz"""
        krisha_link = self.cleaned_data.get('krisha_link')
        if krisha_link:
            # Проверяем, что ссылка содержит krisha.kz
            if 'krisha.kz' not in krisha_link.lower():
                raise forms.ValidationError("Ссылка должна быть с сайта Krisha.kz")
            
            # Проверяем формат ссылки
            if not krisha_link.startswith(('http://', 'https://')):
                raise forms.ValidationError("Ссылка должна начинаться с http:// или https://")
            
            # Проверяем длину ссылки
            if len(krisha_link) > 500:
                raise forms.ValidationError("Ссылка слишком длинная")
        
        return krisha_link

    def clean_complex_name(self):
        """Валидация поля жилого комплекса"""
        complex_name = self.cleaned_data.get('complex_name')
        if complex_name and not complex_name.is_active:
            raise forms.ValidationError("Выберите активный жилой комплекс")
        return complex_name
    
    def clean(self):
        """Общая валидация формы - проверка обязательных полей"""
        cleaned_data = super().clean()
        
        # Список обязательных полей согласно требованиям
        required_fields = {
            'rooms_count': 'Количество комнат',
            'price': 'Цена',
            'repair_status': 'Ремонт',
            'building_type': 'Тип дома',
            'year_built': 'Год постройки',
            'floor': 'Этаж',
            'total_floors': 'Этажность дома',
            'area': 'Площадь',
            'microdistrict': 'Микрорайон'
        }
        
        errors = {}
        for field_name, field_label in required_fields.items():
            if not cleaned_data.get(field_name):
                errors[field_name] = f"Поле '{field_label}' обязательно для заполнения"
        
        if errors:
            for field, error in errors.items():
                self.add_error(field, error)
        
        return cleaned_data

    def save(self, commit=True):
        # Get address data from form fields
        address_data = self.get_address_data()
        
        # Create or get address
        address, created = Address.objects.get_or_create(**address_data)
        
        # Set address to announcement
        announcement = super().save(commit=False)
        announcement.address = address
        
        # Save model field values as strings for backward compatibility
        repair_status_obj = self.cleaned_data.get('repair_status')
        building_type_obj = self.cleaned_data.get('building_type')
        
        if repair_status_obj:
            announcement.repair_status = repair_status_obj.name
        if building_type_obj:
            announcement.building_type = building_type_obj.name
        
        if commit:
            announcement.save()
            # Handle ManyToMany field landmarks after object is saved
            landmarks = self.cleaned_data.get('landmarks')
            if landmarks:
                announcement.landmarks.set(landmarks)
            else:
                announcement.landmarks.clear()
            # Save any remaining ManyToMany fields
            self.save_m2m()
        
        return announcement


class CollectionForm(forms.ModelForm):
    """Collection creation/edit form"""
    
    class Meta:
        model = Collection
        fields = ['name']
        labels = {
            'name': 'Название коллекции'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название коллекции'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Название коллекции должно содержать не менее 2 символов")
        return name.strip()


class SearchForm(forms.Form):
    """Advanced search form for announcements based on the mockup"""
    
    # Количество комнат - кнопки
    ROOMS_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5+', '5+'),
    ]
    
    # Микрорайон - будет заполнен динамически в __init__
    MICRODISTRICT_CHOICES = [
        ('', 'Выберите микрорайон'),
    ]
    
    # Тип дома - будет заполнен динамически в __init__
    BUILDING_TYPE_CHOICES = [
        ('', 'Выберите тип дома'),
    ]
    
    # Количество комнат - множественный выбор
    rooms_count = forms.MultipleChoiceField(
        choices=ROOMS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rooms-checkbox'
        })
    )
    
    # Цена
    price_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'от'
        })
    )
    
    price_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до'
        })
    )
    
    # Цена за м²
    price_per_sqm_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'от'
        })
    )
    
    price_per_sqm_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до'
        })
    )
    
    # Микрорайон
    microdistrict = forms.ChoiceField(
        choices=MICRODISTRICT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Тип дома
    building_type = forms.ChoiceField(
        choices=BUILDING_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Год постройки
    year_built_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'от'
        })
    )
    
    year_built_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до'
        })
    )
    
    # Жилой комплекс
    complex_name = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Площадь
    area_from = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'от',
            'step': '0.1'
        })
    )
    
    area_to = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до',
            'step': '0.1'
        })
    )
    
    # Этаж
    floor_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'от'
        })
    )
    
    floor_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до'
        })
    )
    
    # Чекбоксы
    not_first_floor = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    not_last_floor = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Показать только новостройки
    is_new_building = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Показать только предложения от агентства
    agency_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Показать только предложения где партнер дополнительно платит вознаграждение"
    )
    
    # Фильтр по агентству
    agency = forms.ModelChoiceField(
        queryset=Agency.objects.all(),
        required=False,
        empty_label="Все агентства",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Фильтр по опорным точкам
    LANDMARK_CHOICES = [
        ('', 'Все опорные точки'),
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
    
    landmarks = forms.ModelMultipleChoiceField(
        queryset=Landmark.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Импортируем модели
        from .models import Microdistrict, BuildingType, ResidentialComplex
        from django.core.cache import cache
        
        # 🚀 Кэшированные choices для микрорайонов
        microdistrict_choices_key = 'search_form_microdistrict_choices_v2'
        microdistrict_choices = cache.get(microdistrict_choices_key)
        if not microdistrict_choices:
            microdistrict_choices = [('', 'Выберите микрорайон')]
            microdistricts = Microdistrict.objects.filter(is_active=True).order_by('name')
            for microdistrict in microdistricts:
                microdistrict_choices.append((microdistrict.name, microdistrict.name))
            cache.set(microdistrict_choices_key, microdistrict_choices, 3600)  # 1 час
        self.fields['microdistrict'].choices = microdistrict_choices
        
        # 🚀 Кэшированные choices для типов домов с сортировкой "иной" вверху
        building_type_choices_key = 'search_form_building_type_choices_v2'
        building_type_choices = cache.get(building_type_choices_key)
        if not building_type_choices:
            building_type_choices = [('', 'Выберите тип дома')]
            building_types = BuildingType.objects.filter(is_active=True).extra(
                select={'is_other': "CASE WHEN LOWER(name) = 'иной' THEN 0 ELSE 1 END"}
            ).order_by('is_other', 'name')
            for building_type in building_types:
                building_type_choices.append((building_type.name, building_type.name))
            cache.set(building_type_choices_key, building_type_choices, 3600)  # 1 час
        self.fields['building_type'].choices = building_type_choices
        
        # 🚀 Кэшированные choices для жилых комплексов
        complex_choices_key = 'search_form_complex_choices_v2'
        complex_choices = cache.get(complex_choices_key)
        if not complex_choices:
            complex_choices = [('', 'Все жилые комплексы')]
            complexes = ResidentialComplex.objects.filter(is_active=True).extra(
                select={'name_sort': "CASE WHEN name ~ '^[А-Яа-я]' THEN '1' || name ELSE '2' || name END"}
            ).order_by('name_sort')
            for complex_obj in complexes:
                complex_choices.append((complex_obj.name, complex_obj.name))
            cache.set(complex_choices_key, complex_choices, 3600)  # 1 час
        self.fields['complex_name'].choices = complex_choices


class ChangeAgencyForm(forms.Form):
    """Form for changing user's agency"""
    
    agency_name = forms.CharField(
        label="Название агентства",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название нового агентства'
        }),
        help_text="Если агентство не существует, оно будет создано автоматически"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Установить текущее агентство как значение по умолчанию
        if self.user and self.user.agency:
            self.fields['agency_name'].initial = self.user.agency.name
    
    def clean_agency_name(self):
        agency_name = self.cleaned_data.get('agency_name')
        
        if not agency_name:
            raise forms.ValidationError("Название агентства не может быть пустым.")
        
        # Проверяем, что пользователь не пытается изменить на то же агентство
        if self.user and self.user.agency and agency_name == self.user.agency.name:
            raise forms.ValidationError("Вы уже состоите в этом агентстве.")
        
        return agency_name.strip()
    
    def save(self, user):
        """
        Сохранить изменения агентства пользователя
        Возвращает словарь с информацией о результате
        """
        agency_name = self.cleaned_data['agency_name']
        old_agency = user.agency
        
        # Попытаемся найти существующее агентство
        agency, created = Agency.objects.get_or_create(
            name=agency_name,
            defaults={'name': agency_name}
        )
        
        # Обновляем агентство пользователя
        user.agency = agency
        user.save()
        
        return {
            'old_agency': old_agency,
            'agency': agency,
            'created': created
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите старый пароль'})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите новый пароль'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите новый пароль'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Старый пароль введён неверно.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', 'Пароли не совпадают.')
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data['new_password1']
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user


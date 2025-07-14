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
            'placeholder': '7(XXX)-XXX-XXXX',
            'autofocus': True,
            'data-mask': '7(000)-000-0000'
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
                'placeholder': '7(XXX)-XXX-XXXX',
                'data-mask': '7(000)-000-0000'
            }),
            'additional_phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '7(XXX)-XXX-XXXX (необязательно)',
                'data-mask': '7(000)-000-0000'
            }),
            'whatsapp_phone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '7(XXX)-XXX-XXXX (необязательно)',
                'data-mask': '7(000)-000-0000'
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
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(XXX)-XXX-XXXX")
        
        return phone
    
    def clean_additional_phone(self):
        phone = self.cleaned_data.get('additional_phone')
        if phone:
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                phone = '+' + phone_digits
            else:
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(XXX)-XXX-XXXX")
        return phone
    
    def clean_whatsapp_phone(self):
        phone = self.cleaned_data.get('whatsapp_phone')
        if phone:
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                phone = '+' + phone_digits
            else:
                raise forms.ValidationError("Пожалуйста, введите номер телефона в формате 7(XXX)-XXX-XXXX")
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
        required=True,
        label="Улица *",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название улицы'
        })
    )
    
    building_no = forms.CharField(
        required=True,
        label="Номер дома *",
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
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'style': 'width: 150px; display: inline-block;'
        }),
        label="Сумма тенге"
    )
    
    commission_bonus = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'style': 'width: 150px; display: inline-block;'
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

    class Meta:
        model = Announcement
        fields = [
            'rooms_count', 'price', 'repair_status', 'building_type',
            'year_built', 'is_new_building', 'floor', 'total_floors',
            'area', 'description', 'landmarks', 'krisha_link', 'commission_type',
            'commission_percentage', 'commission_amount', 'commission_bonus'
        ]
        labels = {
            'rooms_count': 'Количество комнат *',
            'price': 'Цена *',
            'year_built': 'Год постройки *',
            'is_new_building': 'Новостройка',
            'floor': 'Этаж *',
            'total_floors': 'Всего этажей *',
            'area': 'Площадь *',
            'description': 'Описание *',
            'landmarks': 'Дом находится рядом с:'
        }
        widgets = {
            'rooms_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': 'Введите количество комнат',
                'required': True
            }),
            'price': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите цену в тенге',
                'required': True,
                'inputmode': 'numeric'
            }),
            'year_built': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': 2030,
                'placeholder': 'Введите год постройки',
                'required': True
            }),
            'is_new_building': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'floor': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Этаж',
                'required': True
            }),
            'total_floors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Всего этажей',
                'required': True
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'placeholder': 'Введите площадь в м²',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите описание недвижимости',
                'required': True
            }),
            'landmarks': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
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
        
        # Set querysets for model choice fields
        self.fields['microdistrict'].queryset = Microdistrict.objects.filter(is_active=True).order_by('name')
        self.fields['complex_name'].queryset = ResidentialComplex.objects.filter(is_active=True).order_by('name')
        self.fields['repair_status'].queryset = RepairType.objects.filter(is_active=True).order_by('name')
        self.fields['building_type'].queryset = BuildingType.objects.filter(is_active=True).order_by('name')

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
            # Убираем форматирование (точки)
            price_str = str(price).replace('.', '').replace(' ', '')
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

    def clean_complex_name(self):
        """Валидация поля жилого комплекса"""
        complex_name = self.cleaned_data.get('complex_name')
        if complex_name and not complex_name.is_active:
            raise forms.ValidationError("Выберите активный жилой комплекс")
        return complex_name

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
    
    # Микрорайон
    MICRODISTRICT_CHOICES = [
        ('', 'Выберите микрорайон'),
        ('almaty', 'Алматы'),
        ('baikonyr', 'Байконыр'),
        ('esil', 'Есиль'),
        ('saryarka', 'Сарыарка'),
        ('nura', 'Нура'),
    ]
    
    # Тип дома - выпадающий список
    BUILDING_TYPE_CHOICES = [
        ('', 'Выберите тип дома'),
        ('кирпичный', 'Кирпичный'),
        ('панельный', 'Панельный'),
        ('монолитный', 'Монолитный'),
        ('иной', 'Иной'),
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
        })
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
        
        # Динамически заполняем choices для жилых комплексов
        complex_choices = [('', 'Все жилые комплексы')]
        
        # Получаем уникальные названия жилых комплексов из базы данных
        from .models import Address
        complexes = Address.objects.filter(
            complex_name__isnull=False
        ).exclude(
            complex_name__exact=''
        ).values_list('complex_name', flat=True).distinct().order_by('complex_name')
        
        for complex_name in complexes:
            complex_choices.append((complex_name, complex_name))
            
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


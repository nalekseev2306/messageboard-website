from django import forms
from django.core.exceptions import ValidationError
from .models import Ad, Category

class MultipleFileInput(forms.ClearableFileInput):
    """Кастомный виджет для загрузки нескольких файлов"""
    allow_multiple_selected = True
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def value_from_datadict(self, data, files, name):
        """Возвращаем список всех загруженных файлов"""
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return [files.get(name)]


class MultipleFileField(forms.FileField):
    """Кастомное поле для работы со списком файлов"""
    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', {})
        kwargs.setdefault("widget", MultipleFileInput(attrs))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """Обрабатываем список файлов вместо одного"""
        if not data:
            return []
        
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = []
            for d in data:
                if d:
                    cleaned = single_file_clean(d, initial)
                    if cleaned:
                        result.append(cleaned)
            return result
        else:
            result = single_file_clean(data, initial)
            return [result] if result else []


class AdForm(forms.ModelForm):
    """Форма объявления"""

    images = MultipleFileField(
        label='Изображения',
        required=False,
        help_text='Выберите до 4 изображений (JPG, PNG, GIF)'
    )
    
    files = MultipleFileField(
        label='Дополнительные файлы',
        required=False,
        help_text='Выберите до 4 файлов (PDF, DOC, TXT, XLS)'
    )

    class Meta:
        model = Ad
        fields = [
            'title', 'description', 'category', 'ad_type',
            'price', 'city', 'published_until'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Что-нибудь привлекательное и информативное...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Подробное описание товара или услуги...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'ad_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Москва'
            }),
            'published_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'ГГГГ-ММ-ДД'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['published_until'].required = False
        self.fields['published_until'].help_text = 'Оставьте пустым для автоматической установки (30 дней)'
        self.fields['price'].required = False
        self.fields['price'].help_text = 'Оставьте пустым, если не требуется'
    
    def clean_price(self):
        """Валидация цены"""
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError('Цена не может быть отрицательной.')
            if price > 999999999:
                raise ValidationError('Цена не может превышать 999 999 999 ₽.')
        return price
    
    def clean_images(self):
        """Валидация количества и размера изображений"""
        images = self.cleaned_data.get('images', [])
        
        if len(images) > 4:
            raise ValidationError('Можно загрузить не более 4 изображений.')
        
        max_size = 5 * 1024 * 1024
        for image in images:
            if image.size > max_size:
                raise ValidationError(f'Изображение "{image.name}" превышает максимальный размер 5 МБ.')
        
        return images
    
    def clean_files(self):
        """Валидация файлов"""
        files = self.cleaned_data.get('files', [])
        
        if len(files) > 4:
            raise ValidationError('Можно загрузить не более 4 файлов.')
        
        max_size = 10 * 1024 * 1024
        for file in files:
            if file.size > max_size:
                raise ValidationError(f'Файл "{file.name}" превышает максимальный размер 10 МБ.')
        return files


class SearchForm(forms.Form):
    """Форма поиска"""

    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите слово для поиска...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.CharField(
        required=False,
        label='Город',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Город'
        })
    )
    ad_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + list(Ad.AD_TYPE_CHOICES),
        required=False,
        label='Тип объявления',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

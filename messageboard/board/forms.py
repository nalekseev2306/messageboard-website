from django import forms
from django.core.exceptions import ValidationError
from .models import Ad, Category

class AdForm(forms.ModelForm):
    """Форма объявления"""

    class Meta:
        model = Ad
        fields = [
            'title', 'description', 'category', 'ad_type',
            'price', 'city', 'published_until', 'main_image'
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
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем некоторые поля необязательными
        self.fields['main_image'].required = False
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

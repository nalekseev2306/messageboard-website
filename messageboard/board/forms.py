from django import forms
from .models import Ad, Category

class AdForm(forms.ModelForm):
    """Форма объявления"""

    class Meta:
        model = Ad
        fields = [
            'title', 'description', 'category', 'ad_type',
            'price', 'contact_name', 'contact_phone', 'contact_email',
            'city', 'published_until', 'main_image'
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
                'placeholder': '0'
            }),
            # позже будем брать из профиля
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван Иванов'
            }),
            # позже будем брать из профиля
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 XXX XXX-XX-XX'
            }),
            # позже будем брать из профиля
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
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
        self.fields['contact_email'].required = False
        self.fields['main_image'].required = False
        self.fields['published_until'].required = False
        self.fields['published_until'].help_text = 'Оставьте пустым для автоматической установки (30 дней)'
        self.fiels['price'].required = False
        self.fields['price'].help_text = 'Оставьте пустым, если не требуется'



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

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    
    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message="Введите номер телефона в формате: +7XXXXXXXXXX"
    )
    
    phone = forms.CharField(
        label='Телефон',
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX'
        })
    )
    
    city = forms.CharField(
        label='Город',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Москва'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'city', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования профиля"""
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'city', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()

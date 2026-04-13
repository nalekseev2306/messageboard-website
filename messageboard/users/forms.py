from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .validators import phone_regex

User = get_user_model()


class BaseUserForm(forms.ModelForm):
    """Базовый класс с общими полями и валидацией"""

    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    phone = forms.CharField(
        label='Телефон',
        required=True,
        validators=[phone_regex],
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '+7XXXXXXXXXX'}
        ),
    )

    city = forms.CharField(
        label='Город',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Москва'}
        ),
    )

    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'email@example.com'}
        ),
    )

    first_name = forms.CharField(
        label='Имя',
        required=False,
        min_length=2,
        max_length=20,
        error_messages={
            'min_length': 'Имя должно содержать минимум 2 символа',
            'max_length': 'Имя не может быть длиннее 20 символов',
        },
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Иван'}
        ),
    )

    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        min_length=2,
        max_length=20,
        error_messages={
            'min_length': 'Фамилия должна содержать минимум 2 символа',
            'max_length': 'Фамилия не может быть длиннее 20 символов',
        },
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Иванов'}
        ),
    )

    @staticmethod
    def validate_name(value, field_name):
        """Общая валидация имени/фамилии"""
        if value and any(char.isdigit() for char in value):
            raise ValidationError(f'{field_name} не может содержать цифры')
        return value

    def clean_first_name(self):
        return self.validate_name(self.cleaned_data.get('first_name'), 'Имя')

    def clean_last_name(self):
        return self.validate_name(
            self.cleaned_data.get('last_name'), 'Фамилия'
        )

    class Meta:
        abstract = True


class CustomUserCreationForm(UserCreationForm, BaseUserForm):
    """Форма регистрации пользователя"""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'email',
            'phone',
            'city',
            'first_name',
            'last_name',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Пароль'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Подтверждение пароля'}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(BaseUserForm, UserChangeForm):
    """Форма редактирования профиля с проверкой уникальности username"""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'phone',
            'city',
            'first_name',
            'last_name',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()
        self.fields['phone'].required = False

    def clean_username(self):
        """Проверка уникальности username"""
        username = self.cleaned_data.get('username')
        if (
            username
            and User.objects.filter(username=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return username

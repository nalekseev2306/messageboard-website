from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError

from users.constants import (
    MAX_NAME_LENGTH,
    MIN_NAME_LENGTH,
    MSG_NAME_MAX_LEGTH,
    MSG_NAME_MIN_LEGTH,
    MSG_NAME_VALIDATE,
    MSG_USERNAME_TAKEN,
)
from users.validators import phone_regex

User = get_user_model()


class BaseUserForm(forms.ModelForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    phone = forms.CharField(
        label='Телефон',
        required=True,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7XXXXXXXXXX'}),
    )
    city = forms.CharField(
        label='Город',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Москва'}),
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
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        error_messages={
            'min_length': MSG_NAME_MIN_LEGTH.format(field='Имя', length=MIN_NAME_LENGTH),
            'max_length': MSG_NAME_MAX_LEGTH.format(field='Имя', length=MAX_NAME_LENGTH),
        },
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
    )
    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        error_messages={
            'min_length': MSG_NAME_MIN_LEGTH.format(field='Фамилия', length=MIN_NAME_LENGTH),
            'max_length': MSG_NAME_MAX_LEGTH.format(field='Фамилия', length=MAX_NAME_LENGTH),
        },
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
    )

    @staticmethod
    def validate_name(value, field_name):
        if value and any(char.isdigit() for char in value):
            raise ValidationError(MSG_NAME_VALIDATE.format(field=field_name))
        return value

    def clean_first_name(self):
        return self.validate_name(self.cleaned_data.get('first_name'), 'Имя')

    def clean_last_name(self):
        return self.validate_name(self.cleaned_data.get('last_name'), 'Фамилия')

    class Meta:
        abstract = True


class UserCreationForm(BaseUserCreationForm, BaseUserForm):
    class Meta(BaseUserCreationForm.Meta):
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


class UserChangeForm(BaseUserForm, BaseUserChangeForm):
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
        username = self.cleaned_data.get('username')
        if (
            username and
            User.objects.filter(username=username).exclude(pk=self.instance.pk).exists()
        ):
            raise ValidationError(MSG_USERNAME_TAKEN)
        return username

from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+7\d{10}$',
    message='Номер телефона должен быть в формате: +7XXXXXXXXXX',
)

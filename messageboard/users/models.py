from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import phone_regex


class User(AbstractUser):
    """Расширенная модель пользователя"""

    # Телефон
    phone = models.CharField(
        'Телефон',
        max_length=12,
        validators=[phone_regex],
        blank=True,
        null=True,
        unique=True,
        help_text='В формате +7XXXXXXXXXX',
    )

    # Город
    city = models.CharField(
        'Город',
        max_length=50,
        blank=True,
        null=True,
        help_text='Ваш город проживания',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    def save(self, *args, **kwargs):
        if self.phone:
            import re

            self.phone = re.sub(r'[\s\-\(\)]', '', self.phone)
        super().save(*args, **kwargs)

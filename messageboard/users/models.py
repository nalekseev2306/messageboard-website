import re

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (
    CLEAR_PHONE_REGEX,
    HELP_TEXT_CITY,
    HELP_TEXT_PHONE,
    MAX_CITY_LENGTH,
    MAX_PHONE_LENGTH,
)


class User(AbstractUser):
    phone = models.CharField(
        'Телефон',
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        null=True,
        unique=True,
        help_text=HELP_TEXT_PHONE,
    )
    city = models.CharField(
        'Город',
        max_length=MAX_CITY_LENGTH,
        blank=True,
        null=True,
        help_text=HELP_TEXT_CITY,
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
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = re.sub(CLEAR_PHONE_REGEX, '', self.phone)
        super().save(*args, **kwargs)

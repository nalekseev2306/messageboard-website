from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Расширенная модель пользователя"""
    
    # Контактная информация
    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message="Номер телефона должен быть в формате: +7XXXXXXXXXX"
    )
    phone = models.CharField(
        'Телефон',
        max_length=12,
        validators=[phone_regex],
        blank=True,
        null=True,
        unique=True,
        help_text='В формате +7XXXXXXXXXX'
    )
    
    # Город
    city = models.CharField(
        'Город',
        max_length=50,
        blank=True,
        null=True,
        help_text='Ваш город проживания'
    )
    
    # # Дополнительная информация
    # avatar = models.ImageField(
    #     'Аватар',
    #     upload_to='avatars/%Y/%m/',
    #     blank=True,
    #     null=True,
    #     help_text='Рекомендуемый размер: 200x200 пикселей'
    # )
    
    # bio = models.TextField(
    #     'О себе',
    #     max_length=500,
    #     blank=True,
    #     null=True,
    #     help_text='Расскажите немного о себе'
    # )
    
    # total_ads = models.PositiveIntegerField(
    #     'Всего объявлений',
    #     default=0,
    #     editable=False
    # )
    
    # active_ads = models.PositiveIntegerField(
    #     'Активных объявлений',
    #     default=0,
    #     editable=False
    # )
    
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
    
    # def update_ad_counts(self):
    #     """Обновляет счетчики объявлений"""
    #     from board.models import Ad
    #     from django.utils import timezone
        
    #     self.total_ads = self.ads.count()
    #     self.active_ads = self.ads.filter(
    #         is_active=True,
    #         published_until__gt=timezone.now()
    #     ).count()
    #     self.save(update_fields=['total_ads', 'active_ads'])

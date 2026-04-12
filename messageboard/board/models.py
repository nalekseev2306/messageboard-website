from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
from unidecode import unidecode

class Category(models.Model):
    """Модель категорий объявлений"""
    
    # Основные поля
    name = models.CharField('Название категории', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    
    # Сортировка и статус
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    is_active = models.BooleanField('Активна', default=True)
    
    # Мета-информация
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Автоматически создаем slug из названия"""
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('board:category_ads', kwargs={'slug': self.slug})
    

class Ad(models.Model):
    """Модель объявления"""
    
    # Типы объявлений
    AD_TYPE_CHOICES = [
        ('sale', 'Продажа'),
        ('purchase', 'Покупка'),
        ('service', 'Услуги'),
        ('exchange', 'Обмен'),
        ('rent', 'Аренда'),
    ]
    
    # Основная информация
    title = models.CharField('Заголовок', max_length=200, validators=[MinLengthValidator(5)])
    description = models.TextField('Описание', validators=[MinLengthValidator(20)])
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='ads',
        verbose_name='Категория'
    )
    
    # Тип
    ad_type = models.CharField('Тип объявления', max_length=20, choices=AD_TYPE_CHOICES, default='sale')
    
    # Цена
    price = models.DecimalField('Цена', max_digits=10, decimal_places=0, blank=True, null=True)
    
    # Контактная информация
    contact_phone = models.CharField('Телефон для связи', max_length=20)
    contact_email = models.EmailField('Email для связи', blank=True, null=True)
    contact_name = models.CharField('Имя контактного лица', max_length=50, default='Продавец')
    
    # Город
    city = models.CharField('Город', max_length=100, blank=True, null=True)
    
    # Изображения
    main_image = models.ImageField('Главное изображение', upload_to='ads/img/%Y/%m/', blank=True, null=True)
    
    # Статусы объявления
    is_active = models.BooleanField('Активно', default=True)
    
    # Автор
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='ads',
        verbose_name='Автор'
    )
    
    # Статистика
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    published_until = models.DateTimeField('Актуально до', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('board:ad_detail', kwargs={'pk': self.pk})
    
    @property
    def is_expired(self):
        """Проверка на истечение срока актуальности"""
        if self.published_until and timezone.now() > self.published_until:
            return True
        return False
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливаем дату окончания на 30 дней"""
        if not self.published_until:
            self.published_until = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

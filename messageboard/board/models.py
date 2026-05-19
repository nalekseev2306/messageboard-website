from django.conf import settings
from django.core.validators import FileExtensionValidator, MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode

from board.constants import (
    AD_TYPE_CHOICES,
    ALLOWED_FILE_EXTENSIONS,
    MAX_AD_CITY_LENGTH,
    MAX_AD_DESCRIPTION_LENGTH,
    MAX_AD_TITLE_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_CATEGORY_SLUG_LENGTH,
)


class Category(models.Model):
    name = models.CharField('Название категории', max_length=MAX_CATEGORY_NAME_LENGTH, unique=True)
    slug = models.SlugField('URL', max_length=MAX_CATEGORY_SLUG_LENGTH, unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('board:category_ads', kwargs={'slug': self.slug})


class Ad(models.Model):
    title = models.CharField('Заголовок', max_length=MAX_AD_TITLE_LENGTH, validators=[MinLengthValidator(5)])
    description = models.TextField('Описание', max_length=MAX_AD_DESCRIPTION_LENGTH, validators=[MinLengthValidator(20)])
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Категория',
    )
    ad_type = models.CharField(
        'Тип объявления',
        max_length=32,
        choices=AD_TYPE_CHOICES,
        default='sale'
    )
    price = models.DecimalField('Цена', max_digits=10, decimal_places=0, blank=True, null=True)
    city = models.CharField('Город', max_length=MAX_AD_CITY_LENGTH, blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ads',
        verbose_name='Автор',
    )

    is_active = models.BooleanField('Активно', default=True)
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
        if self.published_until and timezone.now() > self.published_until:
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.published_until:
            self.published_until = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


class AdImage(models.Model):
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Объявление',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='ads/img/%Y/%m/',
        help_text='Поддерживаются форматы: JPG, PNG, GIF',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Изображение {self.order + 1} для {self.ad.title}'


class AdFile(models.Model):
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Объявление',
    )
    file = models.FileField(
        'Файл',
        upload_to='ads/files/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_EXTENSIONS)],
        help_text=f'Поддерживаемые форматы: {", ".join(ALLOWED_FILE_EXTENSIONS).upper()}'
    )
    file_size = models.PositiveIntegerField('Размер файла (байт)', editable=False, default=0)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Файл для {self.ad.title}: {self.get_filename()}'

    def get_filename(self):
        return self.file.name.split('/')[-1]

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        name = self.file.name
        return name.split('.')[-1].lower() if '.' in name else ''

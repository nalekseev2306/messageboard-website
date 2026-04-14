from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinLengthValidator, FileExtensionValidator
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
    title = models.CharField(
        'Заголовок', max_length=200, validators=[MinLengthValidator(5)]
    )
    description = models.TextField(
        'Описание', validators=[MinLengthValidator(20)]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Категория',
    )

    # Тип
    ad_type = models.CharField(
        'Тип объявления',
        max_length=20,
        choices=AD_TYPE_CHOICES,
        default='sale'
    )

    # Цена
    price = models.DecimalField(
        'Цена', max_digits=10, decimal_places=0, blank=True, null=True
    )

    # Контактная информация
    contact_phone = models.CharField('Телефон для связи', max_length=20)
    contact_email = models.EmailField('Email для связи', blank=True, null=True)
    contact_name = models.CharField(
        'Имя контактного лица', max_length=50, default='Продавец'
    )

    # Город
    city = models.CharField('Город', max_length=100, blank=True, null=True)

    # Изображения
    main_image = models.ImageField(
        'Главное изображение',
        upload_to='ads/img/%Y/%m/',
        blank=True,
        null=True
    )

    # Статусы объявления
    is_active = models.BooleanField('Активно', default=True)

    # Автор
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ads',
        verbose_name='Автор',
    )

    # Статистика
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    published_until = models.DateTimeField(
        'Актуально до', blank=True, null=True
    )

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


class AdImage(models.Model):
    """Изображения для объявления"""

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
    is_main = models.BooleanField('Главное изображение', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['order', 'created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['ad', 'is_main'],
                condition=models.Q(is_main=True),
                name='unique_main_image_per_ad',
            )
        ]

    def __str__(self):
        return f'Изображение {self.order + 1} для {self.ad.title}'

    def save(self, *args, **kwargs):
        if self.is_main:
            AdImage.objects.filter(ad=self.ad, is_main=True).update(
                is_main=False
            )
        super().save(*args, **kwargs)


class AdFile(models.Model):
    """Файлы для объявления (PDF, DOC, TXT и т.д.)"""

    ALLOWED_EXTENSIONS = [
        '.pdf', '.txt', '.doc',
        '.docx', '.xls', '.xlsx',
        '.zip', '.rar', 'mp4',
        'webm', 'mov',
    ]

    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Объявление',
    )
    file = models.FileField(
        'Файл',
        upload_to='ads/files/%Y/%m/',
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)
        ],
        help_text=(
            f'Поддерживаемые форматы: {", ".join(ALLOWED_EXTENSIONS).upper()}',
        )
    )
    file_size = models.PositiveIntegerField(
        'Размер файла (байт)', editable=False, default=0
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Файл для {self.ad.title}: {self.get_filename()}'

    def get_filename(self):
        """Возвращает имя файла"""
        return self.file.name.split('/')[-1]

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        """Возвращает расширение файла"""
        name = self.file.name
        return name.split('.')[-1].lower() if '.' in name else ''

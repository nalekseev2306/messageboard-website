from django import forms
from django.core.exceptions import ValidationError

from .models import Ad


class MultipleFileInput(forms.ClearableFileInput):
    """Кастомный виджет для загрузки нескольких файлов"""

    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def value_from_datadict(self, data, files, name):
        """Возвращаем список всех загруженных файлов"""
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return [files.get(name)]


class MultipleFileField(forms.FileField):
    """Кастомное поле для работы со списком файлов"""

    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', {})
        kwargs.setdefault('widget', MultipleFileInput(attrs))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """Обрабатываем список файлов вместо одного"""
        if not data:
            return []

        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = []
            for d in data:
                if d:
                    cleaned = single_file_clean(d, initial)
                    if cleaned:
                        result.append(cleaned)
            return result
        else:
            result = single_file_clean(data, initial)
            return [result] if result else []


class AdForm(forms.ModelForm):
    """Форма объявления"""

    ALLOWED_IMAGE_TYPES = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
        ]
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    ALLOWED_FILE_EXTENSIONS = [
            '.pdf', '.txt', '.doc',
            '.docx', '.xls', '.xlsx',
            '.zip', '.rar',
        ]
    ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'webm', 'mov',]
    MAX_VIDEO_SIZE = 50 * 1024 * 1024
    MAX_FILE_SIZE = 10 * 1024 * 1024

    images = MultipleFileField(
        label='Изображения',
        required=False,
        help_text='Выберите до 4 изображений (JPG, PNG, GIF, WEBP)',
    )

    files = MultipleFileField(
        label='Дополнительные файлы',
        required=False,
        help_text='Выберите до 4 файлов (PDF, DOC, XLS, ZIP, MP4)',
    )

    class Meta:
        model = Ad
        fields = [
            'title',
            'description',
            'category',
            'ad_type',
            'price',
            'city',
            'published_until',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': (
                        'Что-нибудь привлекательное и информативное...'
                    ),
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Подробное описание товара или услуги...',
                }
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'ad_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '1'}
            ),
            'city': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Москва'}
            ),
            'published_until': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'ГГГГ-ММ-ДД',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['published_until'].required = False
        self.fields[
            'published_until'
        ].help_text = 'Оставьте пустым для автоматической установки (30 дней)'
        self.fields['price'].required = False
        self.fields['price'].help_text = 'Оставьте пустым, если не требуется'

    def clean_price(self):
        """Валидация цены"""
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError('Цена не может быть отрицательной.')
            if price > 999999999:
                raise ValidationError('Цена не может превышать 999 999 999 ₽.')
        return price

    def clean_images(self):
        """Валидация количества, размера и типа изображений"""
        images = self.cleaned_data.get('images', [])

        if len(images) > 4:
            raise ValidationError('Можно загрузить не более 4 изображений.')

        for image in images:
            image_name = image.name.lower()
            image_extension = image_name.split('.')[-1]
            content_type = getattr(image, 'content_type', '')

            if image.size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    f'Изображение "{image_name}" превышает '
                    f'максимальный размер 10 МБ.'
                )

            is_valid = False
            if content_type in self.ALLOWED_IMAGE_TYPES:
                is_valid = True
            else:
                if image_extension in self.ALLOWED_IMAGE_EXTENSIONS:
                    is_valid = True

            if not is_valid:
                raise ValidationError(
                    f'Файл "{image_name}" имеет неподдерживаемый формат. '
                    f'Разрешены: JPG, JPEG, PNG, GIF, WEBP.'
                )

        return images

    def clean_files(self):
        """Валидация количества, размера и типа файлов"""
        files = self.cleaned_data.get('files', [])

        if len(files) > 4:
            raise ValidationError('Можно загрузить не более 4 файлов.')

        for file in files:
            file_name = file.name.lower()
            file_extension = file_name.split('.')[-1]

            if file_extension in self.ALLOWED_VIDEO_EXTENSIONS:
                if file.size > self.MAX_VIDEO_SIZE:
                    raise ValidationError(
                        f'Видеофайл "{file.name}" превышает '
                        f'максимальный размер 50 МБ.'
                    )

            if file.size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    f'Файл "{file.name}" превышает максимальный размер 10 МБ.'
                )

            if file_extension not in (
                self.ALLOWED_FILE_EXTENSIONS + self.ALLOWED_VIDEO_EXTENSIONS
            ):
                raise ValidationError(
                    f'Файл "{file.name}" имеет неподдерживаемый формат. '
                    f'Разрешены: PDF, TXT, DOC, DOCX, XLS, XLSX, ZIP, '
                    f'RAR, MP4, MOV, WEBM.'
                )

        return files

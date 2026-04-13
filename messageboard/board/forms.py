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

    images = MultipleFileField(
        label='Изображения',
        required=False,
        help_text='Выберите до 4 изображений (JPG, PNG, GIF, WEBP)',
    )

    files = MultipleFileField(
        label='Дополнительные файлы',
        required=False,
        help_text='Выберите до 4 файлов (PDF, DOC, TXT, XLS, ZIP)',
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
                    'placeholder': 'Что-нибудь привлекательное и информативное...',
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

        ALLOWED_IMAGE_TYPES = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
        ]
        ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

        if len(images) > 4:
            raise ValidationError('Можно загрузить не более 4 изображений.')

        max_size = 5 * 1024 * 1024
        for image in images:
            if image.size > max_size:
                raise ValidationError(
                    f'Изображение "{image.name}" превышает максимальный размер 5 МБ.'
                )

            content_type = getattr(image, 'content_type', '')
            file_name = image.name.lower()

            is_valid = False
            if content_type in ALLOWED_IMAGE_TYPES:
                is_valid = True
            else:
                for ext in ALLOWED_IMAGE_EXTENSIONS:
                    if file_name.endswith(ext):
                        is_valid = True
                        break

            if not is_valid:
                raise ValidationError(
                    f'Файл "{image.name}" имеет неподдерживаемый формат. '
                    f'Разрешены: JPG, JPEG, PNG, GIF, WEBP.'
                )

        return images

    def clean_files(self):
        """Валидация количества, размера и типа файлов"""
        files = self.cleaned_data.get('files', [])

        ALLOWED_FILE_EXTENSIONS = [
            '.pdf',
            '.txt',
            '.doc',
            '.docx',
            '.xls',
            '.xlsx',
            '.zip',
            '.rar',
        ]

        if len(files) > 4:
            raise ValidationError('Можно загрузить не более 4 файлов.')

        max_size = 10 * 1024 * 1024
        for file in files:
            if file.size > max_size:
                raise ValidationError(
                    f'Файл "{file.name}" превышает максимальный размер 10 МБ.'
                )

            file_name = file.name.lower()

            is_valid = False
            for ext in ALLOWED_FILE_EXTENSIONS:
                if file_name.endswith(ext):
                    is_valid = True
                    break

            if not is_valid:
                raise ValidationError(
                    f'Файл "{file.name}" имеет неподдерживаемый формат. '
                    f'Разрешены: PDF, TXT, DOC, DOCX, XLS, XLSX, ZIP, RAR.'
                )

        return files

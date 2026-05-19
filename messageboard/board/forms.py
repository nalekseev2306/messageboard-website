from django import forms
from django.core.exceptions import ValidationError

from board.constants import (
    ALLOWED_FILE_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_IMAGE_TYPES,
    MAX_FILE_SIZE,
    MSG_CAPACITY_FILES,
    MSG_CAPACITY_IMAGES,
    MSG_CAPACITY_PRICE,
    MSG_FILE_EXTENSION_ERROR,
    MSG_FILE_SIZE_ERROR,
    MSG_NEGATIVE_PRICE,
)
from board.models import Ad


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return [files.get(name)]


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', {})
        kwargs.setdefault('widget', MultipleFileInput(attrs))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
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
                    'placeholder': ('Что-нибудь привлекательное и информативное...'),
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
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Москва'}),
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
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError(MSG_NEGATIVE_PRICE)
            if price > 999_999_999:
                raise ValidationError(MSG_CAPACITY_PRICE)
        return price

    def clean_images(self):
        images = self.cleaned_data.get('images', [])

        if len(images) > 4:
            raise ValidationError(MSG_CAPACITY_IMAGES)

        for image in images:
            image_name = image.name.lower()
            image_extension = image_name.split('.')[-1]
            content_type = getattr(image, 'content_type', '')

            if image.size > MAX_FILE_SIZE:
                raise ValidationError(
                    MSG_FILE_SIZE_ERROR.format(name=image_name, size=MAX_FILE_SIZE)
                )

            is_valid = False
            if content_type in ALLOWED_IMAGE_TYPES:
                is_valid = True
            else:
                if image_extension in ALLOWED_IMAGE_EXTENSIONS:
                    is_valid = True

            if not is_valid:
                raise ValidationError(
                    MSG_FILE_EXTENSION_ERROR.format(
                        name=image_name, extensions=', '.join(ALLOWED_IMAGE_EXTENSIONS).upper()
                    )
                )

        return images

    def clean_files(self):
        files = self.cleaned_data.get('files', [])

        if len(files) > 4:
            raise ValidationError(MSG_CAPACITY_FILES)

        for file in files:
            file_name = file.name.lower()
            file_extension = file_name.split('.')[-1]

            if file.size > MAX_FILE_SIZE:
                raise ValidationError(
                    MSG_FILE_SIZE_ERROR.format(name=file.name, size=MAX_FILE_SIZE)
                )

            if file_extension not in ALLOWED_FILE_EXTENSIONS:
                raise ValidationError(
                    MSG_FILE_EXTENSION_ERROR.format(
                        name=file.name, extensions=', '.join(ALLOWED_FILE_EXTENSIONS).upper()
                    )
                )

        return files

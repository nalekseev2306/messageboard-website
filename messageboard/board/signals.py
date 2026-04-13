from django.core.files.storage import default_storage
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import AdImage, AdFile


@receiver(pre_delete, sender=AdImage)
def delete_ad_image_file(sender, instance, **kwargs):
    """Удаляет файл изображения при удалении записи"""
    if instance.image and default_storage.exists(instance.image.name):
        default_storage.delete(instance.image.name)


@receiver(pre_delete, sender=AdFile)
def delete_ad_file(sender, instance, **kwargs):
    """Удаляет файл при удалении записи"""
    if instance.file and default_storage.exists(instance.file.name):
        default_storage.delete(instance.file.name)


def register_signals():
    """Функция для регистрации сигналов"""
    pass

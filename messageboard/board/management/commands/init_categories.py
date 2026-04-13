from django.core.management.base import BaseCommand
from board.models import Category


class Command(BaseCommand):
    help = 'Инициализация базовых категорий объявлений'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Недвижимость', 'order': 1},
            {'name': 'Работа', 'order': 2},
            {'name': 'Товары', 'order': 3},
            {'name': 'Спорт', 'order': 4},
            {'name': 'Транспорт', 'order': 5},
            {'name': 'Электроника', 'order': 6},
            {'name': 'Животные', 'order': 7},
            {'name': 'Хобби', 'order': 8},
        ]

        for cat in categories:
            obj, created = Category.objects.get_or_create(
                name=cat['name'], defaults={'order': cat['order']}
            )

            if not obj.slug or obj.slug == '':
                obj.save()
                self.stdout.write(
                    self.style.WARNING(f'Обновлён slug для: {obj.name}')
                )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создана категория: {obj.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Категории успешно инициализированы!')
        )

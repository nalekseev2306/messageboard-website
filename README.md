# Доска объявлений

Веб-приложение для создания и управления доской объявлений. Пользователи могут размещать, искать и фильтровать объявления по различным категориям.

## Технологии

- Python 3.10+
- Django 5.2
- SQLite (разработка)
- Bootstrap 5
- HTML 5

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/nalekseev2306/messageboard-website/
cd messageboard-website
```

### 2. Создание и активация виртуального окружения

```bash
python -m venv venv
source vevn/Scripts/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
cd messageboard
```

### 4. Применение миграций

```bash
python manage.py migrate
```

### 5. Инициализация базовых категорий

```bash
python manage.py init_categories
```

### 6. Загразка фикстуры (для тестирования)

```bash
python manage.py loaddata ../db.json
```

### 7. Запуск приложения

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

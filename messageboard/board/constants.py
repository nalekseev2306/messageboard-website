MAX_CATEGORY_NAME_LENGTH = 32
MAX_CATEGORY_SLUG_LENGTH = 32

MAX_AD_TITLE_LENGTH = 256
MAX_AD_DESCRIPTION_LENGTH = 2048
MAX_AD_CITY_LENGTH = 32
AD_TYPE_CHOICES = [
    ('sale', 'Продажа'),
    ('purchase', 'Покупка'),
    ('service', 'Услуги'),
    ('exchange', 'Обмен'),
    ('rent', 'Аренда'),
]

ALLOWED_IMAGE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
]
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_FILE_EXTENSIONS = [
    'pdf',
    'txt',
    'doc',
    'docx',
    'xls',
    'xlsx',
    'zip',
    'rar',
    'mp4',
    'webm',
    'mov',
]
MAX_FILE_SIZE = 10 * 1024 * 1024

PAGE_SIZE = 9

AD_LIST_TITLE = 'Главная - Доска объявлений'
DETAIL_TITLE = '{title} - Доска объявлений'
CREATE_TITLE = 'Создать объявление'
CREATE_BUTTON_TEXT = 'Опубликовать'
UPDATE_TITLE = 'Редактировать объявление'
UPDATE_BUTTON_TEXT = 'Сохранить изменения'
CATEGORY_LIST_TITLE = '{category} - Доска объявлений'
ABOUT_TITLE = 'О проекте'

MSG_SUCCESS_CREATE = 'Ваше объявление успешно опубликовано!'
MSG_ERROR_CREATE = 'Пожалуйста, исправьте ошибки в форме'
MSG_SUCCESS_UPDATE = 'Объявление успешно обновлено!'
MSG_ERROR_UPDATE = 'Пожалуйста, исправьте ошибки в форме'
MSG_SUCCESS_DELETE = 'Объявление успешно удалено!'
MSG_SUCCESS_FILE = 'Файл удален'
MSG_ERROR_FILE = 'Превышено максимальное количество изображений. Вы можете загрузить не более 4.'
MSG_SUCCESS_IMAGE = 'Изображение удалено'
MSG_ERROR_IMAGE = 'Превышено максимальное количество файлов. Вы можете загрузить не более 4.'
MSG_PERMISSION_DENIED = 'У вас нет прав на удаление'

MSG_NEGATIVE_PRICE = 'Цена не может быть отрицательной.'
MSG_CAPACITY_PRICE = 'Цена не может превышать 999 999 999 ₽.'
MSG_CAPACITY_IMAGES = 'Можно загрузить не более 4 изображений.'
MSG_CAPACITY_FILES = 'Можно загрузить не более 4 файлов.'
MSG_FILE_SIZE_ERROR = 'Файл "{name}" превышает максимальный размер {size} МБ.'
MSG_FILE_EXTENSION_ERROR = 'Файл "{name}" имеет неподдерживаемый формат. Разрешены: {extensions}.'

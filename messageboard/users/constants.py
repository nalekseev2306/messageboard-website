MAX_PHONE_LENGTH = 12
MAX_CITY_LENGTH = 32
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 32

HELP_TEXT_PHONE = 'В формате +7XXXXXXXXXX'
HELP_TEXT_CITY = 'Ваш город проживания'

PHONE_REGEX = r'^\+7\d{10}$'
CLEAR_PHONE_REGEX = r'[\s\-\(\)]'

MSG_PHONE_REGEX = 'Номер телефона должен быть в формате: +7XXXXXXXXXX'
MSG_SUCCESS_REGISTER = 'Регистрация успешно завершена! Теперь вы можете войти.'
MSG_ERROR_REGISTER = 'Пожалуйста, исправьте ошибки в форме.'
MSG_SUCCESS_PROFILE_EDIT = 'Ваш профиль успешно обновлен!'
MSG_ERROR_PROFILE_EDIT = 'Пожалуйста, исправьте ошибки в форме.'
MSG_SUCCESS_PASSWORD_CHANGE = 'Пароль успешно изменён!'
MSG_USERNAME_TAKEN = 'Пользователь с таким именем уже существует.'
MSG_NAME_MIN_LEGTH = '{field} должно содержать минимум {length} символа'
MSG_NAME_MAX_LEGTH = '{field} не может быть длиннее {length} символов'
MSG_NAME_VALIDATE = '{field} не может содержать цифры'

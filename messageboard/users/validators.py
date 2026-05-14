from django.core.validators import RegexValidator

from users.constants import MSG_PHONE_REGEX, PHONE_REGEX

phone_regex = RegexValidator(
    regex=PHONE_REGEX,
    message=MSG_PHONE_REGEX,
)

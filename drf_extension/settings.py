from django.conf import settings

from rest_framework.settings import APISettings as RESTAPISettings

USER_SETTINGS = getattr(settings, "DRF_EXTENSION", None)

DEFAULTS = {
    'REMOTE_ADDRESS_HEADER': 'REMOTE_IP',

    'DEFAULT_MIDDLEWARE': [
        'drf_extension.cors.middleware.CORSMiddleWare',
        'drf_extension.middleware.RequestBodyTooLargeMiddleware'
    ],

    'ENHANCE_MIDDLEWARE': [
        'drf_extension.middleware.MakeResponseMiddleware',  # this middleware should be last one
    ],

    'EXCEPTION_DATA_HANDLER': 'drf_extension.exceptions.handle_exception_data',
    'EXPOSE_EXCEPTION_STATUS_CODE': True,
    'ERROR_RESPONSE_HEADER': 'Status-Code',
    'ERROR_RESPONSE_FIELD': 'status_code',

    'JSONP_CALLBACK_PARAM': 'jsonp',

    'CORS_ALLOW_ALL_ORIGIN': True,

    'ACCESS_CONTROL_ALLOW_CREDENTIALS': True,
    'ACCESS_CONTROL_ALLOW_HEADERS': [
        'authorization',
        'content-type',
        'x-csrftoken',
        'x-requested-with',
        'cache-control',
        'if-match',
        'if-unmodified-since'
    ],
    'ACCESS_CONTROL_ALLOW_METHODS': ['DELETE', 'PUT', 'PATCH', 'HEAD'],
    'ACCESS_CONTROL_ALLOW_ORIGIN': [],
    'ACCESS_CONTROL_EXPOSE_HEADERS': [],
    'ACCESS_CONTROL_MAX_AGE': 86400,

}


IMPORT_STRINGS = [
    'EXCEPTION_DATA_HANDLER'
]


REMOVED_SETTINGS = []


class APISettings(RESTAPISettings):
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.defaults = DEFAULTS if defaults is None else defaults
        self.import_strings = IMPORT_STRINGS if import_strings is None else import_strings

        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)

        self._cached_attrs = set()

    def __check_user_settings(self, user_settings):
        for setting in user_settings:
            if setting not in self.defaults:
                raise AttributeError("Invalid API setting: '%s' in settings.DRF_EXTENSION" % setting)
        return user_settings


api_setting = APISettings(USER_SETTINGS, None, None)

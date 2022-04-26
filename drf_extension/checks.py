from django.conf import settings
from django.core.checks import register, Tags, Error
from rest_framework.settings import api_settings as rest_api_settings

from drf_extension.settings import api_setting


@register(Tags.security)
def cors_check_settings(app_configs):
    errors = []
    if not api_setting.CORS_ALLOW_ALL_ORIGIN and not api_setting.ACCESS_CONTROL_ALLOW_ORIGIN:
        errors.append(
            Error(
                'CORS_ALLOW_ALL_ORIGIN and ACCESS_CONTROL_ALLOW_ORIGIN can not be both empty.',
                id="drf_extension.E001"
            )
        )
    return errors


@register(Tags.security)
def rest_framework_check_setting(app_configs):
    errors = []
    token_auth = 'rest_framework.authentication.TokenAuthentication'
    token_app = 'rest_framework.authtoken'
    for auth in rest_api_settings.DEFAULT_AUTHENTICATION_CLASSES:
        if token_auth == f'{auth.__module__}.{auth.__name__}':
            if token_app not in settings.INSTALLED_APPS:
                errors.append(
                    Error(
                        'REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES contains "%s", but "%s" not in INSTALLED_APPS' %
                        (token_auth, token_app),
                        id='drf_extension.E002'
                    )
                )
                break
    return errors

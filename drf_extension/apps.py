from django.apps.config import AppConfig
from django.conf import settings

from drf_extension.settings import api_setting


class DRFExtensionConfig(AppConfig):
    name = 'drf_extension'

    def ready(self):
        from drf_extension import checks

        if 'rest_framework' in settings.INSTALLED_APPS:
            from rest_framework.views import APIView
            from drf_extension.views import wrap_finalize_response

            APIView.finalize_response = wrap_finalize_response(APIView.finalize_response)

            rest_framework_settings = getattr(settings, 'REST_FRAMEWORK', {})
            if rest_framework_settings:
                from drf_extension.exceptions import exception_handler
                rest_framework_settings.setdefault('EXCEPTION_HANDLER', exception_handler)

        django_middlewares = settings.MIDDLEWARE

        for index, m in enumerate(api_setting.DEFAULT_MIDDLEWARE):
            django_middlewares.insert(index, m)

        for m in api_setting.ENHANCE_MIDDLEWARE:
            if m not in django_middlewares:
                django_middlewares.append(m)


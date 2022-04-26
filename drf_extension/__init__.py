import os

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.urls.conf import path, include
from django.utils.module_loading import import_module

default_app_config = 'drf_extension.apps.DRFExtensionConfig'


def auto_register_apps_urlpatterns(prefix_path='api/', *, apps_root_dir='.', raise_exception=True):
    if not prefix_path.endswith('/'):
        prefix_path += '/'
    apps_urlpatterns = []
    for app_config in django_apps.get_app_configs():
        app_urls_path = os.path.join(apps_root_dir, app_config.name, 'urls.py')
        if os.path.exists(app_urls_path):
            urls_module_name = '%s.%s' % (app_config.name, 'urls')
            try:
                urls_module = import_module(urls_module_name)
                urlpatterns = getattr(urls_module, 'urlpatterns', None)
                if urlpatterns:
                    apps_urlpatterns.extend(urlpatterns)
                else:
                    raise ImproperlyConfigured(f'{urls_module_name} has no urlpatterns')
            except ModuleNotFoundError as e:
                if raise_exception:
                    raise e
    return [
        path(prefix_path, include(apps_urlpatterns))
    ]

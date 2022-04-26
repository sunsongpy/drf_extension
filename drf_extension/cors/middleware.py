from urllib.parse import urlparse

from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from drf_extension.cors import constant
from drf_extension.settings import api_setting


preflight_request_default_response_headers_mapping = {
    h.replace('-', '_').upper(): h for h in [
        constant.ACCESS_CONTROL_ALLOW_CREDENTIALS,
        constant.ACCESS_CONTROL_ALLOW_HEADERS,
        constant.ACCESS_CONTROL_ALLOW_METHODS,
        constant.ACCESS_CONTROL_MAX_AGE,
    ]
}


class CORSMiddleWare(MiddlewareMixin):

    def __init__(self, get_response):
        super().__init__(get_response)
        self.is_cors_allow_origin = api_setting.CORS_ALLOW_ALL_ORIGIN

        self.cors_expose_headers = api_setting.ACCESS_CONTROL_EXPOSE_HEADERS
        self.cors_allow_credentials = api_setting.ACCESS_CONTROL_ALLOW_CREDENTIALS

    def process_request(self, request):
        if self.is_preflight_request(request.META):
            request._is_preflight_request = True
            response = HttpResponse()
            response['Content-Length'] = 0
            return response

    def process_response(self, request, response):
        if not self.is_cors_request(request):
            return response

        is_preflight = getattr(request, '_is_preflight_request', False)

        if is_preflight:
            for k, v in preflight_request_default_response_headers_mapping.items():
                value = getattr(api_setting, k, None)
                if value:
                    if isinstance(value, (list, tuple)):
                        response[v] = ', '.join(value)
                    else:
                        response[v] = value
        else:
            if self.cors_allow_credentials:
                response[constant.ACCESS_CONTROL_ALLOW_CREDENTIALS] = 'true'
            if self.cors_expose_headers:
                response[constant.ACCESS_CONTROL_EXPOSE_HEADERS] = ', '.join(self.cors_expose_headers)

        if self.is_cors_allow_origin:
            response[constant.ACCESS_CONTROL_ALLOW_ORIGIN] = request.META['HTTP_ORIGIN']
        else:
            response[constant.ACCESS_CONTROL_ALLOW_ORIGIN] = ', '.join(api_setting.ACCESS_CONTROL_ALLOW_ORIGIN)

        return response

    @staticmethod
    def is_preflight_request(environ):
        origin = environ.get('HTTP_ORIGIN')
        method = environ['REQUEST_METHOD'].upper()
        return method == 'OPTIONS' and origin and (
            constant.ACCESS_CONTROL_REQUEST_METHOD in environ or constant.ACCESS_CONTROL_REQUEST_HEADERS in environ
        )

    @staticmethod
    def is_cors_request(request):
        host = request.META.get('HTTP_HOST')
        origin = request.META.get('HTTP_ORIGIN')
        if host and origin:
            return host != urlparse(origin).netloc
        return False

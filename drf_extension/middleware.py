from django.conf import settings

from django.http.response import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin

from drf_extension.views import make_response
from drf_extension.settings import api_setting


class RequestBodyTooLargeMiddleware(MiddlewareMixin):
    max_body_size = settings.DATA_UPLOAD_MAX_MEMORY_SIZE or 0

    def process_request(self, request):
        request_body_size = int(request.META.get('CONTENT_LENGTH') or 0)
        if self.max_body_size < request_body_size:
            return JsonResponse({
                'error': 'Request Body(%s bytes) is too large, exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE(%s bytes).'
                         % (request_body_size, self.max_body_size)
            }, status=413)


class MakeResponseMiddleware(MiddlewareMixin):
    response_class = JsonResponse

    def process_response(self, request, response):
        if isinstance(response, HttpResponse):
            return response
        _response_class = getattr(request, '_response_class', None) or self.response_class
        return make_response(response, response_class=_response_class, safe=False)


class JSONPMiddleware(MiddlewareMixin):
    """
    like https://a.com?jsonp=func_name

    HttpResponse("data") => HttPResponse('func_name("data")')
    """

    def process_response(self, request, response):
        callback_name = self.get_callback_name(request)
        if response.status_code != 200 or not callback_name or response.streaming:
            return response
        self.set_json_padding_response(response, callback_name)
        return response

    @staticmethod
    def get_callback_name(request):
        return request.GET.get(api_setting.JSONP_CALLBACK_PARAM)

    @staticmethod
    def set_json_padding_response(response, callback):
        containers = getattr(response, '_container', [])
        if containers:
            containers.insert(0, (callback + '(').encode())
            containers.append(b')')

            content_length = 0
            for c in containers:
                content_length += len(c)
            response['Content-Length'] = content_length


class SetRemoteAddressMiddleware(MiddlewareMixin):

    @staticmethod
    def get_real_ip(env):
        real_ip = env.get('HTTP_X_REAL_IP', '')
        if not real_ip:
            real_ip = env.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
        return real_ip.strip()

    def process_request(self, request):
        request.META[api_setting.REMOTE_ADDRESS_HEADER] = self.get_real_ip(request.META)


class DownLoadMiddleware(MiddlewareMixin):

    def process_template_response(self, request, response):
        renderer_context = getattr(response, 'renderer_context', None)

        if renderer_context is None or response.status_code != 200 or request.method != 'GET':
            return response
        is_download = request.GET.get('download')
        if is_download:
            renderer_context['indent'] = 4
            self.add_callback(response)
        return response

    @staticmethod
    def add_callback(response):
        renderer_context = response.renderer_context
        accepted_media_type = response.accepted_renderer.media_type

        request = renderer_context['request']

        def patch_content_disposition(resp):
            if resp.has_header('Content-Disposition'):
                return
            resp.setdefault('Content-Length', len(resp.content))

            filename = request.query_params.get('filename') or f'download.{accepted_media_type.split("/")[-1]}'
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'

        response.add_post_render_callback(patch_content_disposition)


class ExceptionMiddleware(MiddlewareMixin):
    is_debug = settings.DEBUG

    def process_exception(self, request, exc):
        if self.is_debug:
            return
        r = JsonResponse(
            {
                'error': str(exc)
            },
            status=500
        )
        return r

from rest_framework import status
from rest_framework.views import exception_handler as rest_exception_handler

from drf_extension.settings import api_setting


def handle_exception_data(data):
    error = data.pop('detail', '') or data
    return {'error': error}


def exception_handler(exc, context):
    response = rest_exception_handler(exc, context)
    if response:
        data = response.data
        data = api_setting.EXCEPTION_DATA_HANDLER(data)
        if not api_setting.EXPOSE_EXCEPTION_STATUS_CODE:
            if api_setting.ERROR_RESPONSE_FIELD:
                data[api_setting.ERROR_RESPONSE_FIELD] = response.status_code
            if api_setting.ERROR_RESPONSE_HEADER:
                response[api_setting.ERROR_RESPONSE_HEADER] = response.status_code
            response.status_code = status.HTTP_200_OK
        response.data = data
    return response

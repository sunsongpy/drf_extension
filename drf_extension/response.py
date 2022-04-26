import os

from django.http.response import FileResponse, JsonResponse


class SimpleFileResponse(FileResponse):
    def __init__(self, filename):
        if not isinstance(filename, str):
            raise ValueError(f'filename {filename} type is not str, but receive {type(filename).__name__}')

        if not os.path.exists(filename):
            raise ValueError(f'filename {filename} does not exists')

        super().__init__(
            open(os.path.abspath(filename), mode='rb'),
            as_attachment=True,
            filename=os.path.basename(filename)
        )


class JSONPResponse(JsonResponse):
    def __init__(self, data):
        super().__init__(data, safe=False, content_type='text/plain')

from rest_framework.decorators import api_view as rest_api_view


def api_view(
        http_method_names=None,
        renderer_classes=None,
        parser_classes=None,
        authentication_classes=None,
        throttle_classes=None,
        permission_classes=None
):

    def wrapper(func):
        if renderer_classes is not None:
            func.renderer_classes = renderer_classes
        if parser_classes is not None:
            func.parser_classes = parser_classes
        if authentication_classes is not None:
            func.authentication_classes = authentication_classes
        if throttle_classes is not None:
            func.throttle_classes = throttle_classes
        if permission_classes is not None:
            func.permission_classes = permission_classes
        return rest_api_view(http_method_names)(func)

    return wrapper

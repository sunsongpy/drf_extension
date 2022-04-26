from rest_framework.pagination import PageNumberPagination as NumberPagination


class PageNumberPagination(NumberPagination):

    page_size_query_param = 'size'

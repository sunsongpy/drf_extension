import graphene


def add_paginate_count_field_to(cls):
    """
    给 DjangoFilterConnectionField 增加 分页的总数字段 count
    :param cls:
    :return:
    """
    connection = getattr(cls._meta, 'connection', None)
    if connection:
        meta = getattr(connection, '_meta', None)
        if meta:
            meta.fields['length'] = graphene.Field(graphene.Int, name='count')
    return cls
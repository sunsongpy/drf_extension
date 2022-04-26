from collections import defaultdict

from django.db import models
from django.utils.functional import cached_property
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_nested_relation_kwargs


def mapping_depth_fields(fields, depth):
    ret = defaultdict(list)
    if not fields or depth is None:
        return ret
    fields = fields.split(',')
    left = []
    for f in fields:
        v = f.split('.', 1)
        if len(v) == 1:
            ret[depth].append(v[0])
        else:
            if v[0] not in ret[depth]:
                ret[depth].append(v[0])
            left.append(v[1])
    ret.update(mapping_depth_fields(','.join(left), depth-1))
    return ret


class ListModelDynamicFieldSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        super().update(instance, validated_data)

    def to_representation(self, data):
        child = self.child
        include_fields = [f for f, c in child.fields.items() if not c.write_only]
        origin_fields = getattr(child, '_origin_fields')
        defer_fields = set(origin_fields) - set(include_fields)

        if isinstance(data, models.Manager):
            try:
                defer_fields.remove(data.field.name)
            except (AttributeError, KeyError):
                pass

        iterable = data.all() if isinstance(data, models.Manager) else data
        if defer_fields and isinstance(iterable, models.QuerySet):
            iterable = iterable.defer(*defer_fields)

        return [
            child.to_representation(item) for item in iterable
        ]


class ModelDynamicFieldSerializer(serializers.ModelSerializer):

    class Meta:
        list_serializer_class = ListModelDynamicFieldSerializer

    @cached_property
    def fields_from_request(self):

        context = self.context
        include_fields = context['request'].query_params.get('include', '')
        return mapping_depth_fields(include_fields, self.Meta.depth)

    def get_field_names(self, declared_fields, info):
        field_names = super().get_field_names(declared_fields, info)

        setattr(self, '_origin_fields', [f for f in field_names if f != self.url_field_name])

        request = self.context.get('request', None)
        if request is None or request.method != 'GET':
            return field_names
        root = self.root
        if hasattr(root, 'child'):
            root = root.child
        fields_from_request = root.fields_from_request[self.Meta.depth]

        return fields_from_request or field_names

    def build_nested_field(self, field_name, relation_info, nested_depth):
        class NestedSerializer(ModelDynamicFieldSerializer):
            class Meta(self.Meta):
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = '__all__'
        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)
        return field_class, field_kwargs

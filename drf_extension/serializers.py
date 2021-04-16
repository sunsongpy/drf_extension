from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init_subclass__(cls, **kwargs):
        meta = cls.Meta
        if not hasattr(meta, 'fields'):
            meta.fields = serializers.ALL_FIELDS
        if getattr(meta, 'depth', None) is None:
            meta.depth = 10
        return super().__init_subclass__()

    @staticmethod
    def get_exact_fields(extra_fields, depth, prefix, flag=True):
        exact_fields = set()
        for field in extra_fields:
            field = field.strip()
            if not field:
                continue

            if depth:
                if field == prefix:
                    exact_fields.clear()
                    exact_fields.add('id')
                    break
                else:
                    fields = field.split('.', depth)
                    if len(fields) >= depth and prefix == fields[depth - 1]:
                        if len(fields) == depth:
                            exact_fields.add('id')
                        else:
                            new_fields = fields[depth].split('.')[0]
                            if new_fields == '*':
                                exact_fields.clear()
                                break
                            else:
                                exact_fields.add(new_fields)
            else:
                if '.' in field:
                    if flag:
                        exact_fields.add(field.split('.')[0])
                else:
                    exact_fields.add(field)
        return exact_fields

    def get_include_fields(self, request, depth, prefix):
        include_fields = request.query_params.get('include', '').split(',')
        return self.get_exact_fields(include_fields, depth, prefix)

    def get_exclude_fields(self, request, depth, prefix):
        exclude_fields = request.query_params.get('exclude', '').split(',')
        return self.get_exact_fields(exclude_fields, depth, prefix, flag=False)

    def get_field_names(self, declared_fields, info):
        request = self.context.get('request')
        fields = super().get_field_names(declared_fields, info)
        if request.method != 'GET' or request is None:
            return fields

        view = self.context['view']
        root_depth = view.serializer_class.Meta.depth
        depth = root_depth - self.Meta.depth
        prefix = getattr(self.Meta, 'prefix', '')

        include = self.get_include_fields(request, depth, prefix)
        exclude = self.get_exclude_fields(request, depth, prefix)

        if include:
            fields = set(fields) & include
        if exclude:
            fields = set(fields) ^ exclude

        return list(fields)

    def build_nested_field(self, field_name, relation_info, nested_depth):
        _, field_kwargs = super().build_nested_field(field_name, relation_info, nested_depth)

        class NestedSerializer(self.__class__):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = '__all__'
                prefix = field_name
        field_class = NestedSerializer
        return field_class, field_kwargs

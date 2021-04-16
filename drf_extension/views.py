from rest_framework.utils import model_meta


def _get_fields_from_query_params(fields):
    fs = set()
    for f in fields.split(','):
        f = f.strip()
        if '.' in f:
            fs.add(f.split('.')[0])
        else:
            fs.add(f)
    return fs


class DynamicFieldViewMix:

    def get_queryset(self):
        select_relate_fields = self.get_select_related_field()
        queryset = super().get_queryset()
        if select_relate_fields:
            queryset = queryset.select_related(*select_relate_fields).all()
        return queryset

    def get_select_related_field(self):
        queryset = getattr(self, 'queryset', None)
        request = getattr(self, 'request', None)
        if queryset is None or request is None:
            return

        model = queryset.model
        select_related_fields = []
        forward_relation_fields = model_meta.get_field_info(model).forward_relations.keys()

        include_fields = request.query_params.get('include', '')
        exclude_fields = request.query_params.get('exclude', '')
        include_fields = _get_fields_from_query_params(include_fields)
        exclude_fields = _get_fields_from_query_params(exclude_fields)

        for i in include_fields:
            if i in forward_relation_fields:
                select_related_fields.append(i)

        for j in exclude_fields:
            if j in forward_relation_fields:
                select_related_fields.remove(j)

        return select_related_fields

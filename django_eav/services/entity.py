from django.db.models.expressions import RawSQL, OrderBy

from django_eav.models import Entity, Value, Attribute


def create(name: str, attr_values: dict[Attribute, any]):
    entity = Entity.objects.create(name=name)
    for attr, value in attr_values.items():
        Value.objects.create(entity=entity, attribute=attr, value=value)
    return entity


def filter_eav(attr_values: dict[Attribute, any]):
    queryset = Entity.objects.all()
    for attr, value in attr_values.items():
        queryset = queryset.filter(value__attribute=attr, value__value=value)
    return queryset.distinct()


def sort(attrs: list[Attribute]):
    queryset = Entity.objects.all()
    for attr in attrs:
        queryset = queryset.filter(
            value__attribute=attr,
            value__isnull=False,
        )
        last_alias = queryset.query.where.children[-1].lhs.alias
        order_by = OrderBy(RawSQL(f"{last_alias}.value", []))
        queryset.query.order_by += (order_by,)
    return queryset

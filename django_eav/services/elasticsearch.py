from elasticsearch_dsl import Search, Q, connections

from django_eav.models import Attribute

es = connections.get_connection()


def create_entity(name: str, attr_values: dict[Attribute, any]):
    es.index(
        index="entities",
        body={
            **{f"attr_{attr.id}": value for attr, value in attr_values.items()},
            "name": name,
        },
        refresh=True,
    )


def filter_entities(attr_values: dict[Attribute, any]):
    s = Search(index="entities")
    must_queries = []
    for attr, value in attr_values.items():
        must_queries.append(Q("term", **{f"attr_{attr.id}": value}))
    query = Q("bool", must=must_queries)
    s = s.query(query)
    return s.execute()


def sort_entities(attrs: list[Attribute]):
    s = Search(index="entities")
    for attr in attrs:
        s = s.sort({f"attr_{attr.id}": {"order": "asc"}})
    return s.execute()

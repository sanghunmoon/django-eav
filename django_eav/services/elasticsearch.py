from elasticsearch_dsl import Document, Text, Keyword, Search, Q, connections

from django_eav.models import Attribute


class EntityDocument(Document):
    name = Text()

    @staticmethod
    def create_attribute(attr_id):
        setattr(EntityDocument, f"attribute_{attr_id}", Keyword())

    @staticmethod
    def update_mapping():
        EntityDocument.init()

    class Index:
        name = "entities"


def create_entity(name: str, attr_values: dict[Attribute, any]):
    entity_doc = EntityDocument(name=name)
    for attr, value in attr_values.items():
        EntityDocument.create_attribute(attr.id)
        setattr(entity_doc, f"attribute_{attr.id}", value)
    entity_doc.save()
    return entity_doc


def filter_entities(attr_values: dict[Attribute, any]):
    s = Search(index="entities")
    query = Q()
    for attr, value in attr_values.items():
        query &= Q("term", **{f"attribute_{attr.id}": value})
    s = s.query(query)
    return s.execute()


def sort_entities(attrs: list[Attribute]):
    s = Search(index="entities")
    for attr in attrs:
        s = s.sort({f"attribute_{attr.id}": {"order": "asc"}})

    return s.execute()

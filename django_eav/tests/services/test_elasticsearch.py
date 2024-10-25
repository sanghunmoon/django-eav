import pytest
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import connections
from django_eav.services.elasticsearch import (
    create_entity,
    filter_entities,
    sort_entities,
    EntityDocument,
)

from django_eav.models import Attribute

pytestmark = pytest.mark.django_db


@pytest.fixture
def attr1():
    return Attribute.objects.create(name="attr1", attribute_type="text")


@pytest.fixture
def attr2():
    return Attribute.objects.create(name="attr2", attribute_type="integer")


@pytest.fixture
def es_connection(attr1, attr2):
    es = Elasticsearch(
        hosts=["https://localhost:9200"],
        http_auth=("elastic", "i0AXYscuuO4xHIt6zOxO"),
        verify_certs=False,
    )
    connections.create_connection(
        hosts=["https://localhost:9200"],
        http_auth=("elastic", "i0AXYscuuO4xHIt6zOxO"),
        verify_certs=False,
    )
    EntityDocument.create_attribute(attr1.id)
    EntityDocument.create_attribute(attr2.id)
    EntityDocument.update_mapping()
    es.indices.delete(index="entities", ignore=[400, 404])
    yield es
    es.indices.delete(index="entities", ignore=[400, 404])


def test_create_entity(attr1, attr2, es_connection):
    entity_doc = create_entity("entity1", {attr1: "value1", attr2: 1})

    assert entity_doc.name == "entity1"
    assert getattr(entity_doc, f"attribute_{attr1.id}") == "value1"
    assert getattr(entity_doc, f"attribute_{attr2.id}") == 1

    search = Search(index="entities").query(
        "match", **{f"attribute_{attr1.id}": "value1"}
    )
    response = search.execute()

    assert len(response.hits) == 1
    assert response.hits[0].name == "entity1"


def test_filter_entities(es_connection):
    attr1 = Attribute.objects.create(name="attr1", attribute_type="text")
    attr2 = Attribute.objects.create(name="attr2", attribute_type="integer")

    entity1 = create_entity("entity1", {attr1: "value1", attr2: 1})
    create_entity("entity2", {attr1: "value1", attr2: 2})
    create_entity("entity3", {attr1: "value2", attr2: 1})
    create_entity("entity4", {attr1: "value2", attr2: 2})

    filtered_entities = filter_entities({attr1: "value1", attr2: 1})

    assert len(filtered_entities.hits) == 1
    assert filtered_entities.hits[0].name == "entity1"


def test_sort_entities(es_connection):
    attr1 = Attribute.objects.create(name="attr1", attribute_type="integer")

    create_entity("entity1", {attr1: 3})
    create_entity("entity2", {attr1: 2})
    create_entity("entity3", {attr1: 4})
    create_entity("entity4", {attr1: 1})

    sorted_entities = sort_entities([attr1])

    sorted_names = [entity.name for entity in sorted_entities.hits]
    assert sorted_names == ["entity4", "entity2", "entity1", "entity3"]

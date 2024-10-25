import pytest
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl import connections

from django_eav.models import Attribute
from django_eav.services.elasticsearch import (
    create_entity,
    filter_entities,
    sort_entities,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def attr1():
    return Attribute.objects.create(name="attr1", attribute_type="text")


@pytest.fixture
def attr2():
    return Attribute.objects.create(name="attr2", attribute_type="integer")


@pytest.fixture(autouse=True)
def es_connection(attr1, attr2):
    es = Elasticsearch(
        hosts=["https://localhost:9200"],
        verify_certs=False,
    )
    connections.create_connection(
        hosts=["https://localhost:9200"],
        verify_certs=False,
    )
    index = Index("entities")
    if not index.exists():
        index.create()
        index.put_mapping(
            body={
                "properties": {
                    f"attr_{attr1.id}": {"type": attr1.attribute_type},
                    f"attr_{attr2.id}": {"type": attr2.attribute_type},
                }
            }
        )
    else:
        es.delete_by_query(index="entities", body={"query": {"match_all": {}}})
    yield es
    index.delete()


def test_create_entity(attr1, attr2):
    create_entity("entity1", {attr1: "value1", attr2: 1})

    search = Search(index="entities").query("match", **{f"attr_{attr1.id}": "value1"})
    response = search.execute()

    assert len(response.hits) == 1
    assert response.hits[0].name == "entity1"


def test_filter_entities(attr1, attr2):
    create_entity("entity1", {attr1: "value1", attr2: 1})
    create_entity("entity2", {attr1: "value1", attr2: 2})
    create_entity("entity3", {attr1: "value2", attr2: 1})
    create_entity("entity4", {attr1: "value2", attr2: 2})

    filtered_entities = filter_entities({attr1: "value1", attr2: 1})

    assert len(filtered_entities.hits) == 1
    assert filtered_entities.hits[0].name == "entity1"


def test_sort_entities(attr1, attr2):
    create_entity("entity1", {attr2: 3})
    create_entity("entity2", {attr2: 2})
    create_entity("entity3", {attr2: 4})
    create_entity("entity4", {attr2: 1})

    sorted_entities = sort_entities([attr2])

    sorted_names = [entity.name for entity in sorted_entities.hits]
    assert sorted_names == ["entity4", "entity2", "entity1", "entity3"]

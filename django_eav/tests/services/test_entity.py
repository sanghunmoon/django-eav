import pytest

from django_eav.models import Attribute
from django_eav.services.entity import create, sort, filter_eav

pytestmark = pytest.mark.django_db


@pytest.mark.django_db(transaction=True)
def test_create_entity():
    entity = create(
        "entity1",
        {
            Attribute.objects.create(name="attr1", attribute_type="text"): "value1",
            Attribute.objects.create(name="attr2", attribute_type="integer"): 1,
        },
    )
    assert entity.name == "entity1"
    assert entity.value_set.count() == 2
    assert entity.value_set.get(attribute__name="attr1").value == "value1"
    assert entity.value_set.get(attribute__name="attr2").value == 1


def test_filter():
    attr1 = Attribute.objects.create(name="attr1", attribute_type="text")
    attr2 = Attribute.objects.create(name="attr2", attribute_type="integer")
    entity1 = create("entity1", {attr1: "value1", attr2: 1})
    create("entity2", {attr1: "value1", attr2: 2})
    create("entity3", {attr1: "value2", attr2: 1})
    create("entity4", {attr1: "value2", attr2: 2})
    entities = filter_eav({attr1: "value1", attr2: 1})
    assert entities.count() == 1
    assert entities[0] == entity1


def test_sort():
    attr1 = Attribute.objects.create(name="attr1", attribute_type="integer")
    entity1 = create("entity1", {attr1: 3})
    entity2 = create("entity2", {attr1: 2})
    entity3 = create("entity3", {attr1: 4})
    entity4 = create("entity4", {attr1: 1})
    entities = sort([attr1])
    assert list(entities) == [entity4, entity2, entity1, entity3]
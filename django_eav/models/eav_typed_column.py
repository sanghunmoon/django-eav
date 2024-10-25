# example of typed column approach
from django.db import models


class Entity(models.Model):
    name = models.CharField(max_length=64)


class Attribute(models.Model):
    name = models.CharField(max_length=64)
    attribute_type = models.CharField(max_length=100)


class Value(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    text_value = models.CharField(max_length=255)
    integer_value = models.IntegerField()
    float_value = models.FloatField()
    date_value = models.DateTimeField()
    boolean_value = models.BooleanField()

    @property
    def value(self):
        if self.attribute.attribute_type == "text":
            return self.text_value
        if self.attribute.attribute_type == "integer":
            return self.integer_value
        if self.attribute.attribute_type == "float":
            return self.float_value
        if self.attribute.attribute_type == "date":
            return self.date_value
        if self.attribute.attribute_type == "boolean":
            return self.boolean_value
        raise None

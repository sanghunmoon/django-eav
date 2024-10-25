from django.db import models


class Entity(models.Model):
    name = models.CharField(max_length=64)


class Attribute(models.Model):
    name = models.CharField(max_length=64)
    attribute_type = models.CharField(max_length=100)


class Value(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.JSONField()

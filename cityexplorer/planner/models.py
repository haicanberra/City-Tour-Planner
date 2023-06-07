from django.db import models
from django.utils import timezone


# Create your models here.
class Marker(models.Model):
    city = models.CharField(max_length=100, null=True)
    places = models.JSONField(default=dict)

    def __str__(self):
        return self.city


class Search(models.Model):
    city = models.CharField(max_length=100, null=True)
    documented = models.CharField(max_length=100, null=True)
    tourism_filters = models.CharField(max_length=100, null=True)
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.city


class Address(models.Model):
    address = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.address


class Path(models.Model):
    paths = models.CharField(max_length=500, null=True)
    query = models.JSONField(default=list)

    def __str__(self):
        return self.paths

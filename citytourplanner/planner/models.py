from django.db import models
from django.utils import timezone

# Create your models here.
class Search(models.Model):
    address = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.address
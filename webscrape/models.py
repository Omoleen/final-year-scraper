from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class SavedProducts(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    store = models.CharField(max_length=10)
    link = models.URLField()
    image = models.URLField()
    price = models.FloatField()

    class Meta:
        unique_together = ["account", "link"]

    def __str__(self):
        return self.name


    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
            return url


class TrendSearch(models.Model):
    search = models.CharField(max_length=100)
    # store = models.JSONField()
    link = models.CharField(max_length=200)
    stores = ArrayField(
        ArrayField(
            models.CharField(max_length=10, blank=True),
            size=8,
        ),
        size=8,
    )

    def __str__(self):
        return self.search
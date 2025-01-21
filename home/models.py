from django.db import models


class Param(models.Model):
    key = models.CharField(max_length=25)
    value = models.CharField(max_length=50)



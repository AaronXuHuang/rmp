from multiprocessing.sharedctypes import Value
from django.db import models

# Create your models here.
class JiraProject(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    key = models.CharField(max_length=50, null=True, blank=True)

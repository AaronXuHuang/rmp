from multiprocessing.sharedctypes import Value
from django.db import models

# Create your models here.
class JiraProject(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    key = models.CharField(max_length=50, null=True, blank=True)


class JiraReleaseObject(models.Model):
    releaseobject = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=50, null=True, blank=True)
    updatetime = models.DateTimeField(auto_now_add=True)

from multiprocessing.sharedctypes import Value
from django.db import models

# Create your models here.
class JiraProject(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    key = models.CharField(max_length=50, null=True, blank=True)


class JiraFixVersion(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    projectid = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    released = models.CharField(max_length=200, null=True, blank=True)


class JiraReleaseObject(models.Model):
    releaseobject = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=50, null=True, blank=True)
    projectid = models.CharField(max_length=50, null=True, blank=True)
    updatetime = models.DateTimeField(auto_now_add=True)

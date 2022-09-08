from django.db import models

# Create your models here.
class ReleaseObject(models.Model):
    fixversion = models.CharField(max_length=50, null=True, blank=True)
    releaseobject = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=50, null=True, blank=True)
    orgunit = models.CharField(max_length=50, null=True, blank=True)
    stage = models.CharField(max_length=50, null=True, blank=True)
    creator = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    released = models.BooleanField(default=False)


class ReleaseProcess(models.Model):
    orgunit = models.CharField(max_length=50, null=True, blank=True)
    fixversion = models.CharField(max_length=50, null=True, blank=True)
    tracker = models.TextField(max_length=50, null=True, blank=True)
    
from django.db import models

# Create your models here.
class OctoSpace(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)

class OctoProject(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    projectgroupid = models.CharField(max_length=50, null=True, blank=True)
    spaceid = models.CharField(max_length=50, null=True, blank=True)
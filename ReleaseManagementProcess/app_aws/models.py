from django.db import models

# Create your models here.
class AWSCredential(models.Model):
    servername = models.CharField(max_length=100, null=True, blank=True)
    updatetime = models.DateTimeField(max_length=100, null=True, blank=True)

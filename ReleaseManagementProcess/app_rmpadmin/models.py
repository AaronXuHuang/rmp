from django.db import models

# Create your models here.
class Orgunit(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)


class Tier(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    orgunit = models.ForeignKey(Orgunit, models.DO_NOTHING, max_length=50, null=True, blank=True)


class Component(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    tier = models.ForeignKey(Tier, models.DO_NOTHING, max_length=50, null=True, blank=True)


class Partner(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    orgunit = models.ForeignKey(Orgunit, models.DO_NOTHING, max_length=50, null=True, blank=True)
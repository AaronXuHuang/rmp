from asyncio.windows_events import NULL
from django.db import models

# Create your models here.
class F5Pools(models.Model):
    env_choices=(
        (1, "DEV"),
        (2, "INT"),
        (3, "QA"),
        (4, "QA3"),
        (5, "QA4"),
        (6, "PIE"),
        (7, "PRF"),
        (8, "HFP"),
        (9, "HFQ"),
        (10, "STG"),
        (99, "PROD"),
    )
    name = models.CharField(max_length=100)
    project = models.CharField(max_length=20)
    server = models.CharField(max_length=100)
    environment = models.SmallIntegerField(choices=env_choices, default='')

class F5PoolMembers(models.Model):
    name = models.CharField(max_length=100)
    poolname = models.ForeignKey(F5Pools, models.DO_NOTHING, max_length=100, null=True, blank=True)
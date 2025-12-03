from django.db import models
from common.mixins.timestamp import TimestampMixin


class ClassType(TimestampMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'class_types'
        ordering = ['name']

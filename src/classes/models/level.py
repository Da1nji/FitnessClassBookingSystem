from django.db import models
from common.mixins.timestamp import TimestampMixin


class Level(TimestampMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    difficulty_order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'levels'
        ordering = ['difficulty_order']

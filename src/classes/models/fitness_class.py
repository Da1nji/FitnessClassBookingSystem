from django.db import models
from .level import Level
from .class_type import ClassType
from instructors.models import Instructor
from common.mixins.timestamp import TimestampMixin


class FitnessClass(TimestampMixin, models.Model):
    class_type = models.ForeignKey(
        ClassType,
        on_delete=models.PROTECT,
        related_name='classes'
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.PROTECT,
        related_name='classes',
        default=1
    )

    duration_minutes = models.PositiveIntegerField(default=60)
    max_capacity = models.PositiveIntegerField(default=20)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes'
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.class_type.name}"

    class Meta:
        db_table = 'fitness_classes'
        verbose_name_plural = 'Fitness Classes'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time', 'is_active']),
            models.Index(fields=['class_type', 'level']),
        ]

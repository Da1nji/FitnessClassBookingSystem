from datetime import timedelta
from django.db import models
from .level import Level
from .class_type import ClassType
from .booking import Booking
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

    @property
    def available_spots(self):
        """Get count of available spots"""
        confirmed_bookings = self.bookings.filter(
            status__in=['confirmed']
        ).count()
        return max(0, self.max_capacity - confirmed_bookings)

    @property
    def is_fully_booked(self):
        """Returns true if all spots are booked"""
        return self.available_spots <= 0

    @property
    def can_be_booked(self):
        """Get a user's booking possibility"""
        from django.utils import timezone
        return (
            self.is_active
            and not self.is_cancelled
            and not self.is_fully_booked
            and self.start_time > timezone.now() + timedelta(hours=1)
        )

    @property
    def confirmed_bookings_count(self):
        """Get count of confirmed bookings"""
        return self.bookings.filter(status__in=['confirmed', 'attended']).count()

    @property
    def pending_bookings_count(self):
        """Get count of pending bookings"""
        return self.bookings.filter(status='pending').count()

    def get_user_booking(self, user):
        """Get a user's booking for this class if it exists"""
        try:
            return self.bookings.get(user=user)
        except Booking.DoesNotExist:
            return None

    def is_user_booked(self, user):
        """Check if a user has booked this class"""
        return self.bookings.filter(
            user=user,
            status__in=['pending', 'confirmed']
        ).exists()

    def __str__(self):
        return f"{self.id} {self.class_type.name}"

    class Meta:
        db_table = 'fitness_classes'
        verbose_name_plural = 'Fitness Classes'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time', 'is_active']),
            models.Index(fields=['class_type', 'level']),
        ]

from datetime import timedelta
from django.db import models
from django.conf import settings


class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    fitness_class = models.ForeignKey(
        "classes.FitnessClass",
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='pending'
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    confirmation_token = models.CharField(max_length=100, unique=True, blank=True)
    is_email_confirmed = models.BooleanField(default=False)

    class Meta:
        db_table = 'bookings'
        unique_together = ['user', 'fitness_class']
        ordering = ['-booked_at']
        indexes = [
            models.Index(fields=['status', 'fitness_class']),
            models.Index(fields=['user', 'booked_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.fitness_class.class_type.name}"

    def save(self, *args, **kwargs):
        if not self.confirmation_token:
            import secrets
            self.confirmation_token = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)

    @property
    def is_confirmed(self):
        return self.status == 'confirmed' and self.is_email_confirmed

    @property
    def can_cancel(self):
        from django.utils import timezone
        return (self.status in ['pending', 'confirmed']
                and self.fitness_class.start_time > timezone.now() + timedelta(hours=2))

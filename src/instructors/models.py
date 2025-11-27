from django.db import models
from django.contrib.auth.models import User
from common.mixins.timestamp import TimestampMixin
from django.conf import settings


class Instructor(TimestampMixin, models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'instructor'}
    )
    bio = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        db_table = 'instructors'

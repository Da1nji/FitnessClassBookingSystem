from django.contrib.auth.models import AbstractUser
from django.db import models
from common.mixins.timestamp import TimestampMixin


class User(TimestampMixin, AbstractUser):
    USER_TYPES = [
        ('member', 'Member'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='member')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    health_notes = models.TextField(blank=True)

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        db_table = 'users'

    @property
    def full_name(self):
        return self.get_full_name()

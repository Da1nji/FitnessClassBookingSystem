import django_filters
from django.db import models
from .models import Instructor


class InstructorFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    name = django_filters.CharFilter(method='filter_name')

    class Meta:
        model = Instructor
        fields = [
            'name',
            'is_active',
        ]

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            models.Q(user__first_name__icontains=value),
            models.Q(user__last_name__icontains=value),
            models.Q(user__username__icontains=value)
        )

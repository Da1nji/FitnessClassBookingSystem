import django_filters
from .models import FitnessClass


class FitnessClassFilter(django_filters.FilterSet):
    is_upcoming = django_filters.BooleanFilter(method='filter_is_upcoming')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = FitnessClass
        fields = [
            'class_type',
            'level',
            'instructor',
            'is_active',
        ]

    def filter_is_upcoming(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(start_time__gt=timezone.now())
        return queryset

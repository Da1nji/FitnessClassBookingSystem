from django.contrib import admin
from .models import Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active']
    list_filter = ['is_active',]
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_editable = ['is_active']

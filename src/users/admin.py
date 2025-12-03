from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FitnessProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'user_type', 'phone', 'is_active',
    ]

    list_filter = [
        'user_type', 'is_active', 'is_superuser',
    ]

    search_fields = [
        'username', 'email', 'first_name', 'last_name',
        'phone',
    ]

    list_editable = ['is_active', 'user_type']

    list_per_page = 25

    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': (
                'user_type', 'phone', 'date_of_birth',
                'emergency_contact', 'emergency_phone',
                'health_notes',
                'is_verified', 'avatar'
            )
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': (
                'user_type', 'phone', 'date_of_birth', 'email'
            )
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    actions = ['activate_users', 'deactivate_users', 'make_instructors']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"

    def make_instructors(self, request, queryset):
        queryset.update(user_type='instructor')
    make_instructors.short_description = "Mark selected users as instructors"


@admin.register(FitnessProfile)
class FitnessProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'primary_goal', 'experience_level',
        'bmi', 'bmi_category', 'is_complete', 'total_workouts'
    ]
    list_filter = [
        'primary_goal', 'experience_level', 'activity_level',
        'bmi_category', 'has_injuries'
    ]
    search_fields = [
        'user__username', 'user__email',
        'user__first_name', 'user__last_name'
    ]
    readonly_fields = [
        'bmi', 'bmi_category', 'is_complete',
        'llm_prompt_context', 'created_at', 'updated_at'
    ]
    autocomplete_fields = ['user', 'preferred_class_types']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Physical Metrics', {
            'fields': ('height_cm', 'weight_kg', 'bmi', 'bmi_category')
        }),
        ('Goals and Experience', {
            'fields': ('primary_goal', 'experience_level', 'months_experience')
        }),
        ('Activity and Preferences', {
            'fields': ('preferred_duration_min', 'days_per_week')
        }),
        ('Health Information', {
            'fields': ('has_injuries', 'injuries_description', 'medical_conditions')
        }),
        ('Equipment and Access', {
            'fields': ('home_equipment',)
        }),
        ('Tracking and History', {
            'fields': ('last_workout_date', 'workout_streak', 'total_workouts')
        }),
        ('LLM Integration', {
            'fields': ('llm_prompt_context', 'last_llm_update'),
            'classes': ('collapse',)
        }),
    )

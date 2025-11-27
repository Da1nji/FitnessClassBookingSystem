from django.contrib import admin
from .models import FitnessClass, ClassType, Level


@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'class_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

    def class_count(self, obj):
        return obj.classes.count()
    class_count.short_description = 'Classes'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty_order', 'class_count', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['difficulty_order']

    def class_count(self, obj):
        return obj.classes.count()
    class_count.short_description = 'Classes'


@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = [
        'class_type', 'level', 'instructor',
        'start_time', 'is_active', 'is_cancelled'
    ]
    list_filter = ['class_type', 'level', 'is_active', 'is_cancelled', 'instructor']
    search_fields = [
        'class_type__name',
        'description',
        'instructor__user__first_name',
        'instructor__user__last_name']
    list_editable = ['is_active']
    date_hierarchy = 'start_time'
    autocomplete_fields = ['class_type', 'level', 'instructor']

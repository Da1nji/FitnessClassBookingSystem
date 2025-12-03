from django.contrib import admin
from .models import FitnessClass, ClassType, Level, Booking
from .services import BookingEmailService


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


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'fitness_class__class_type__name', 'status', 'is_email_confirmed',
        'booked_at', 'confirmed_at'
    ]
    list_filter = ['status', 'is_email_confirmed', 'fitness_class__class_type__name']
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
    ]
    list_editable = ['status']
    readonly_fields = ['booked_at', 'confirmed_at', 'cancelled_at', 'confirmation_token']

    actions = ['send_confirmation_emails', 'mark_as_attended', 'mark_as_no_show']

    def send_confirmation_emails(self, request, queryset):
        for booking in queryset:
            try:
                BookingEmailService.send_booking_confirmation_email(booking)
            except Exception as e:
                self.message_user(request, f"Failed to send email for {
                                  booking}: {e}", level='error')
        self.message_user(request, f"Confirmation emails sent for {queryset.count()} bookings.")
    send_confirmation_emails.short_description = "Send confirmation emails"

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


class BookingEmailService:
    @staticmethod
    def send_booking_confirmation_email(booking):
        try:
            subject = f"Booking Confirmation - {booking.fitness_class.name}"

            context = {
                'user': booking.user,
                'booking': booking,
                'fitness_class': booking.fitness_class,
                'confirmation_url': (f"{settings.FRONTEND_URL or 'http://localhost:8000'}"
                                     "/api/classes/bookings/{booking.id}/confirm/"
                                     "?token={booking.confirmation_token}"),
                'cancellation_url': (f"{settings.FRONTEND_URL or 'http://localhost:8000'}"
                                     "/api/classes/bookings/{booking.id}/cancel"),
            }

            html_message = render_to_string('emails/booking_confirmation.html', context)
            plain_message = strip_tags(html_message)

            sent_count = send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Confirmation email sent to {booking.user.email} for booking {booking.id}")
            return sent_count > 0

        except Exception as e:
            logger.error(f"Failed to send confirmation email for booking {booking.id}: {e}")
            raise

    @staticmethod
    def send_booking_cancellation_email(booking):
        subject = f"Booking Cancelled - {booking.fitness_class.class_type.name}"

        context = {
            'user': booking.user,
            'booking': booking,
            'fitness_class': booking.fitness_class,
        }

        html_message = render_to_string('emails/booking_cancellation.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_class_reminder_email(booking):
        """Send reminder 24 hours before class"""
        subject = f"Class Reminder - {booking.fitness_class.class_type.name}"

        context = {
            'user': booking.user,
            'booking': booking,
            'fitness_class': booking.fitness_class,
        }

        html_message = render_to_string('emails/class_reminder.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.utils import timezone
from ..models import Booking
from ..serializers import (
    BookingReadSerializer,
    BookingCreateSerializer,
)
from ..services import BookingEmailService


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Booking.objects.select_related(
                'user', 'fitness_class', 'fitness_class__class_type',
                'fitness_class__level', 'fitness_class__instructor'
            ).all()
        else:
            return Booking.objects.select_related(
                'user', 'fitness_class', 'fitness_class__class_type',
                'fitness_class__level', 'fitness_class__instructor'
            ).filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.save()

        email_sent = False
        try:
            BookingEmailService.send_booking_confirmation_email(booking)
            email_sent = True
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")

        read_serializer = BookingReadSerializer(
            booking,
            context={'request': request}
        )

        response_data = read_serializer.data
        response_data['email_sent'] = email_sent

        if not email_sent:
            response_data['email_warning'] = 'Email not sent. Use confirmation link below.'

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'get'])
    def confirm(self, request, pk=None):
        """Confirm booking via email link (supports GET and POST)"""
        booking = self.get_object()

        if request.method == 'POST':
            token = request.data.get('token')
        else:
            token = request.query_params.get('token')

        if not token:
            return Response(
                {'error': 'Confirmation token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.confirmation_token != token:
            return Response(
                {'error': 'Invalid confirmation token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.is_email_confirmed:
            return Response(
                {'error': 'Booking already confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.is_email_confirmed = True
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()

        return Response({
            'success': True,
            'message': 'Booking confirmed successfully!',
            'booking': BookingReadSerializer(booking, context={'request': request}).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()

        if not (request.user.is_staff or booking.user == request.user):
            return Response(
                {'error': 'You can only cancel your own bookings'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not booking.can_cancel:
            return Response(
                {'error': 'This booking cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()

        try:
            BookingEmailService.send_booking_cancellation_email(booking)
        except Exception as e:
            print(f"Failed to send cancellation email: {e}")

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get user's upcoming bookings"""
        queryset = self.get_queryset().filter(
            fitness_class__start_time__gt=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('fitness_class__start_time')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get user's booking history"""
        queryset = self.get_queryset().filter(
            fitness_class__start_time__lt=timezone.now()
        ).order_by('-fitness_class__start_time')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

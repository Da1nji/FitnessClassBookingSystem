from ..models import Booking, FitnessClass
from rest_framework import serializers
from .fitness_classes import FitnessClassReadSerializer
from users.serializers import UserReadSerializer


class BookingReadSerializer(serializers.ModelSerializer):
    user_details = UserReadSerializer(source='user', read_only=True)
    fitness_class_details = FitnessClassReadSerializer(source='fitness_class', read_only=True)
    confirmation_link = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_details', 'fitness_class', 'fitness_class_details',
            'status', 'booked_at', 'confirmed_at', 'cancelled_at', 'is_email_confirmed',
            'confirmation_token', 'confirmation_link',
            'is_confirmed', 'can_cancel'
        ]
        read_only_fields = [
            'id', 'booked_at', 'confirmed_at', 'cancelled_at',
            'is_confirmed', 'can_cancel', 'confirmation_token'
        ]

    def get_confirmation_link(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                f'/api/classes/bookings/{obj.id}/confirm/?token={obj.confirmation_token}'
            )
        return None


class BookingCreateSerializer(serializers.ModelSerializer):
    fitness_class_id = serializers.PrimaryKeyRelatedField(
        queryset=FitnessClass.objects.filter(is_active=True),
        source='fitness_class',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'fitness_class_id',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        fitness_class = data['fitness_class']
        user = self.context['request'].user

        if not fitness_class.can_be_booked:
            raise serializers.ValidationError("This class cannot be booked at the moment.")

        if Booking.objects.filter(
            user=user,
            fitness_class=fitness_class,
            status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError("You already have a booking for this class.")

        if fitness_class.is_fully_booked:
            raise serializers.ValidationError("This class is fully booked.")

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

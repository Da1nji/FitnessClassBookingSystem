from rest_framework import serializers
from ..models import Level, ClassType, FitnessClass
from instructors.models import Instructor
from instructors.serializers import InstructorSerializer
from .class_types import ClassTypeSerializer
from .levels import LevelSerializer


class FitnessClassWriteSerializer(serializers.ModelSerializer):
    class_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassType.objects.filter(is_active=True),
        source='class_type',
        write_only=True
    )
    level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        source='level',
        write_only=True
    )
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.filter(is_active=True),
        source='instructor',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = FitnessClass
        fields = [
            'id', 'class_type_id', 'level_id', 'instructor_id',
            'duration_minutes', 'max_capacity', 'price',
            'start_time', 'end_time', 'is_active', 'is_cancelled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Validate that end_time is after start_time
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time"
            })

        expected_duration = (data['end_time'] - data['start_time']).total_seconds() / 60
        if abs(expected_duration - data['duration_minutes']) > 1:  # 1 minute tolerance
            raise serializers.ValidationError({
                "duration_minutes":
                    (f"Duration should be approximately {expected_duration}"
                     " minutes based on start and end times")
            })

        return data


class FitnessClassReadSerializer(serializers.ModelSerializer):
    class_type = ClassTypeSerializer(read_only=True)
    level = LevelSerializer(read_only=True)
    instructor_details = InstructorSerializer(source='instructor', read_only=True)

    is_upcoming = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()
    available_spots = serializers.SerializerMethodField()
    is_fully_booked = serializers.SerializerMethodField()
    can_be_booked = serializers.SerializerMethodField()
    user_has_booking = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        fields = [
            'id', 'class_type', 'level', 'instructor_details',
            'duration_minutes', 'max_capacity', 'price',
            'start_time', 'end_time', 'is_active', 'is_cancelled',
            'is_upcoming', 'is_past', 'available_spots',
            'is_fully_booked', 'can_be_booked', 'user_has_booking',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_is_upcoming(self, obj):
        from django.utils import timezone
        return obj.start_time > timezone.now()

    def get_is_past(self, obj):
        from django.utils import timezone
        return obj.end_time < timezone.now()

    def get_available_spots(self, obj):
        return obj.available_spots

    def get_is_fully_booked(self, obj):
        return obj.is_fully_booked

    def get_can_be_booked(self, obj):
        return obj.can_be_booked

    def get_user_has_booking(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_user_booked(request.user)
        return False

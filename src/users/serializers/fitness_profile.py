from datetime import timezone
from rest_framework import serializers
from ..models import FitnessProfile
from classes.models import ClassType
from .users import UserReadSerializer


class FitnessProfileSerializer(serializers.ModelSerializer):
    preferred_class_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ClassType.objects.filter(is_active=True),
        required=False
    )

    bmi = serializers.FloatField(read_only=True)
    bmi_category = serializers.CharField(read_only=True)
    is_complete = serializers.BooleanField(read_only=True)
    llm_prompt_context = serializers.CharField(read_only=True)

    class Meta:
        model = FitnessProfile
        fields = [
            'height_cm', 'weight_kg', 'bmi', 'bmi_category',

            'primary_goal',
            'activity_level', 'experience_level', 'months_experience',

            'preferred_class_types', 'preferred_times',
            'preferred_duration_min', 'days_per_week',

            'has_injuries', 'injuries_description',
            'medical_conditions', 'home_equipment',

            'last_workout_date', 'workout_streak', 'total_workouts',
            'llm_prompt_context',

            'is_complete', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'last_llm_update',
        ]

    def validate(self, data):
        """Validate fitness profile data"""
        if 'secondary_goals' in data and not isinstance(data['secondary_goals'], list):
            raise serializers.ValidationError({
                "secondary_goals": "Must be a list of goals"
            })

        if 'home_equipment' in data and not isinstance(data['home_equipment'], list):
            raise serializers.ValidationError({
                "home_equipment": "Must be a list of equipment"
            })

        return data

    def create(self, validated_data):
        preferred_class_types = validated_data.pop('preferred_class_types', [])

        profile = FitnessProfile.objects.create(**validated_data)

        if preferred_class_types:
            profile.preferred_class_types.set(preferred_class_types)

        return profile

    def update(self, instance, validated_data):
        old_preferences = {
            'primary_goal': instance.primary_goal,
            'activity_level': instance.activity_level,
            'experience_level': instance.experience_level,
        }

        instance = super().update(instance, validated_data)

        new_preferences = {
            'primary_goal': instance.primary_goal,
            'activity_level': instance.activity_level,
            'experience_level': instance.experience_level,
        }

        if old_preferences != new_preferences:
            instance.preferences_history.append({
                'timestamp': timezone.now().isoformat(),
                'old': old_preferences,
                'new': new_preferences,
                'reason': self.context.get('reason', 'user_update')
            })
            instance.save()

        return instance


class UserWithProfileSerializer(UserReadSerializer):
    """Extended user serializer with fitness profile"""
    fitness_profile = FitnessProfileSerializer(read_only=True)

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + ['fitness_profile']

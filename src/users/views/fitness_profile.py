from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.utils import timezone
from ..models import FitnessProfile
from ..serializers import FitnessProfileSerializer
from classes.serializers import FitnessClassReadSerializer


class FitnessProfileViewSet(viewsets.ModelViewSet):
    serializer_class = FitnessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def get_queryset(self):
        if self.request.user.is_staff:
            return FitnessProfile.objects.all()
        return FitnessProfile.objects.filter(user=self.request.user)

    def _get_profile(self):
        profile, created = FitnessProfile.objects.get_or_create(user=self.request.user)
        return profile

    @action(detail=False, methods=['get', 'put', 'patch'], url_path="mine")
    def mine(self, request):
        profile = self._get_profile()

        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def llm_context(self, request):
        """Get LLM prompt context for this user"""
        profile = self._get_profile()

        return Response({
            'prompt_context': profile.llm_prompt_context,
            'is_complete': profile.is_complete,
            'last_updated': profile.last_llm_update
        })

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        profile = self._get_profile()

        if not profile.is_complete:
            return Response({
                'warning': 'Profile incomplete. Please update height, weight, and goals.',
                'missing_fields': self._get_missing_fields(profile)
            })

        recommendations = self._generate_recommendations(profile)
        suggested_classes = self._get_suggested_classes(profile)

        return Response({
            'recommendations': recommendations,
            'suggested_classes': FitnessClassReadSerializer(suggested_classes, many=True).data
        })

    def _get_missing_fields(self, profile):
        """Get list of missing required fields"""
        missing = []

        if not profile.height_cm or not profile.weight_kg:
            missing.append('height_cm and weight_kg')
        if not profile.primary_goal:
            missing.append('primary_goal')
        if not profile.activity_level:
            missing.append('activity_level')
        if not profile.experience_level:
            missing.append('experience_level')

        return missing

    def _generate_recommendations(self, profile):
        """Generate basic recommendations based on profile"""
        recommendations = []

        if profile.bmi_category == "Overweight" or profile.bmi_category == "Obese":
            recommendations.append({
                'type': 'weight_management',
                'message': 'Focus on cardio and balanced nutrition',
                'priority': 'high'
            })
        elif profile.bmi_category == "Underweight":
            recommendations.append({
                'type': 'nutrition',
                'message': 'Consider strength training and calorie surplus',
                'priority': 'medium'
            })

        if profile.primary_goal == 'weight_loss':
            recommendations.append({
                'type': 'workout',
                'message': 'Focus on HIIT and cardio classes 4-5 times per week',
                'priority': 'high'
            })
        elif profile.primary_goal == 'muscle_gain':
            recommendations.append({
                'type': 'workout',
                'message': 'Focus on strength training with progressive overload',
                'priority': 'high'
            })

        if profile.experience_level == 'beginner':
            recommendations.append({
                'type': 'safety',
                'message': 'Start with beginner-friendly classes and focus on form',
                'priority': 'high'
            })

        return recommendations

    def _get_suggested_classes(self, profile):
        """Get suggested classes based on profile"""
        from classes.models import FitnessClass
        from django.utils import timezone

        queryset = FitnessClass.objects.filter(
            is_active=True,
            is_cancelled=False,
            start_time__gt=timezone.now()
        )

        if profile.preferred_class_types.exists():
            queryset = queryset.filter(
                class_type__in=profile.preferred_class_types.all()
            )

        experience_mapping = {
            'beginner': ['Beginner', 'All Levels'],
            'intermediate': ['Intermediate', 'All Levels'],
            'advanced': ['Advanced', 'All Levels']
        }

        if profile.experience_level in experience_mapping:
            allowed_levels = experience_mapping[profile.experience_level]
            queryset = queryset.filter(level__name__in=allowed_levels)

        return queryset.order_by('start_time')[:5]

    @action(detail=False, methods=['post'])
    def generate_workout_plan(self, request):
        """Generate a personalized workout plan using LLM"""
        from ..services import WorkoutLLMService

        profile = self._get_profile()

        if not profile.is_complete:
            return Response({
                'error': 'Profile incomplete',
                'missing_fields': self._get_missing_fields(profile)
            }, status=status.HTTP_400_BAD_REQUEST)

        days = request.data.get('days', 7)

        try:
            workout_plan = WorkoutLLMService.generate_workout_plan(profile, days)

            if 'error' in workout_plan:
                return Response(workout_plan, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'success': True,
                'workout_plan': workout_plan,
                'generated_at': timezone.now().isoformat(),
            })

        except Exception as e:
            return Response({
                'error': 'Failed to generate workout plan',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

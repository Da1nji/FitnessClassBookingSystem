from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from ..filters import FitnessClassFilter
from ..models import FitnessClass
from ..serializers import (FitnessClassWriteSerializer,
                           FitnessClassReadSerializer)


class FitnessClassViewSet(viewsets.ModelViewSet):
    queryset = FitnessClass.objects.all().select_related(
        'class_type', 'level', 'instructor'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = FitnessClassFilter
    ordering_fields = ['start_time', 'price', 'level']
    ordering = ['start_time']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FitnessClassWriteSerializer
        return FitnessClassReadSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a fitness class
        """
        fitness_class = self.get_object()
        fitness_class.is_cancelled = True
        fitness_class.save()

        serializer = self.get_serializer(fitness_class)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_instructor(self, request, pk=None):
        """
        Assign or change instructor for a class
        """
        fitness_class = self.get_object()
        instructor_id = request.data.get('instructor_id')

        if not instructor_id:
            return Response(
                {"error": "instructor_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from instructors.models import Instructor
            instructor = Instructor.objects.get(id=instructor_id, is_active=True)
            fitness_class.instructor = instructor
            fitness_class.save()

            serializer = self.get_serializer(fitness_class)
            return Response(serializer.data)

        except Instructor.DoesNotExist:
            return Response(
                {"error": "Instructor not found or not active"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get only upcoming classes
        """
        queryset = self.get_queryset().filter(
            start_time__gt=timezone.now(),
            is_active=True,
            is_cancelled=False
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

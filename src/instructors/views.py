from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Instructor
from .serializers import InstructorSerializer
from .filters import InstructorFilter


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.filter(is_active=True)
    serializer_class = InstructorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = InstructorFilter
    search_fields = ['user__username', 'bio']
    ordering_fields = ['user__username']

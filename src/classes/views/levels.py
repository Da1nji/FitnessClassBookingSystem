from rest_framework import viewsets, permissions
from ..models import Level
from ..serializers import LevelSerializer


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Level.objects.all()
        return queryset

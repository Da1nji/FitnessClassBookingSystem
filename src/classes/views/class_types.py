from rest_framework import viewsets, permissions
from ..models import ClassType
from ..serializers import ClassTypeSerializer


class ClassTypeViewSet(viewsets.ModelViewSet):
    queryset = ClassType.objects.all()
    serializer_class = ClassTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = ClassType.objects.all()

        is_active = self.request.query_params.get('is_active', None)
        if is_active and is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active and is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('name')

    def perform_destroy(self, instance):
        """Soft delete by setting is_active to False"""
        instance.is_active = False
        instance.save()

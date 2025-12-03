from rest_framework import serializers
from ..models import ClassType


class ClassTypeSerializer(serializers.ModelSerializer):
    class_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassType
        fields = [
            'id', 'name', 'description', 'is_active',
            'class_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_class_count(self, obj):
        return obj.classes.filter(is_active=True).count()

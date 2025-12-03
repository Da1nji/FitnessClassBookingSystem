from rest_framework import serializers
from ..models import Level


class LevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Level
        fields = [
            'id', 'name', 'description', 'difficulty_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

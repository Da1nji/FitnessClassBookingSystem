from rest_framework import serializers
from users.serializers import UserReadSerializer
from .models import Instructor
from users.models import User


class InstructorSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='instructor'),
        source='user',
        write_only=True
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = [
            'id', 'user', 'user_id', 'full_name', 'bio', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_full_name(self, obj):
        return str(obj)

from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'due_date',
            'completed_at',
            'status',
            'priority'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

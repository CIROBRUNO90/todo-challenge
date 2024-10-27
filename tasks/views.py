from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las tareas para mostrar solo las del usuario actual.
        Permite filtrar por status y priority a través de query params.
        """
        queryset = Task.objects.filter(user=self.request.user)

        status = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        title = self.request.query_params.get('title', None)
        description = self.request.query_params.get('description', None)
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if description:
            queryset = queryset.filter(description__icontains=description)

        return queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Marca una tarea como completada y establece completed_at
        """
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """
        Reabre una tarea completada
        """
        task = self.get_object()
        task.status = 'pending'
        task.completed_at = None
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

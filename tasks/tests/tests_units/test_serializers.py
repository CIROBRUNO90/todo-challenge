import pytest

from django.utils import timezone
from rest_framework.test import APIRequestFactory
from datetime import timedelta

from tasks.models import Task
from tasks.serializers import TaskSerializer
from users.models import Users


@pytest.fixture
def user():
    return Users.objects.create(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def task(user):
    return Task.objects.create(
        title="Test Task",
        description="Test Description",
        status="pending",
        priority="medium",
        user=user
    )


@pytest.fixture
def request_with_user(user):
    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = user
    return request


@pytest.mark.django_db
class TestTaskSerializer:
    def test_contains_expected_fields(self, task):
        """Test serializer contiene todos los campos esperados"""
        serializer = TaskSerializer(task)
        expected_fields = {
            'id', 'title', 'description', 'created_at', 'updated_at',
            'due_date', 'completed_at', 'status', 'priority'
        }
        assert set(serializer.data.keys()) == expected_fields

    def test_read_only_fields(self, task, request_with_user):
        """Test campos read_only no se pueden modificar"""
        data = {
            'title': 'Updated Task',
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
            'completed_at': timezone.now()
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(
            task,
            data=data,
            context=context,
            partial=True
        )
        assert serializer.is_valid()

        updated_task = serializer.save()
        assert updated_task.title == 'Updated Task'
        assert updated_task.created_at == task.created_at
        assert updated_task.completed_at == task.completed_at

    def test_serialization(self, task):
        """Test serialización de una tarea"""
        serializer = TaskSerializer(task)
        data = serializer.data

        assert data['title'] == task.title
        assert data['description'] == task.description
        assert data['status'] == task.status
        assert data['priority'] == task.priority
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_deserialization_valid_data(self, user, request_with_user):
        """Test deserialización con datos válidos"""
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'status': 'pending',
            'priority': 'high',
            'due_date': timezone.now().isoformat()
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(data=data, context=context)

        assert serializer.is_valid()
        task = serializer.save()

        assert task.title == data['title']
        assert task.description == data['description']
        assert task.status == data['status']
        assert task.priority == data['priority']
        assert task.user == user

    def test_invalid_status(self, user, request_with_user):
        """Test validación de un status inválido"""
        data = {
            'title': 'New Task',
            'status': 'invalid_status'
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(data=data, context=context)

        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_invalid_priority(self, user, request_with_user):
        """Test validación de una prioridad inválida"""
        data = {
            'title': 'New Task',
            'priority': 'invalid_priority'
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(data=data, context=context)

        assert not serializer.is_valid()
        assert 'priority' in serializer.errors

    def test_missing_required_fields(self, user, request_with_user):
        """Test validación de campos requeridos faltantes"""
        data = {
            'description': 'Only Description'
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(data=data, context=context)

        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_create_method_assigns_user(self, user, request_with_user):
        """Test método create asigna correctamente el usuario"""
        data = {
            'title': 'New Task',
            'description': 'Test Description',
            'status': 'pending',
            'priority': 'medium'
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(data=data, context=context)

        assert serializer.is_valid()
        task = serializer.save()

        assert task.user == user

    def test_update_preserves_user(self, task, user, request_with_user):
        """Test actualizar una tarea se preserva el usuario original"""
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description'
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(
            task,
            data=data,
            partial=True,
            context=context
        )

        assert serializer.is_valid()
        updated_task = serializer.save()

        assert updated_task.user == task.user

    def test_due_date_format(self, user, request_with_user):
        """Test validación del formato de due_date"""
        valid_date = timezone.now() + timedelta(days=1)
        data = {
            'title': 'Task with Due Date',
            'due_date': valid_date.isoformat()
        }

        context = {'request': request_with_user}
        serializer = TaskSerializer(data=data, context=context)
        assert serializer.is_valid()

        data['due_date'] = 'invalid-date-format'
        serializer = TaskSerializer(data=data, context=context)
        assert not serializer.is_valid()
        assert 'due_date' in serializer.errors

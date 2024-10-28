import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from tasks.models import Task
from users.models import Users


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return Users.objects.create_user(
        username="testuser",
        email="test@test.com",
        password="testpass123"
    )


@pytest.fixture
def other_user():
    return Users.objects.create_user(
        username="otheruser",
        email="other@test.com",
        password="testpass123"
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


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
def other_user_task(other_user):
    return Task.objects.create(
        title="Other User Task",
        description="Other Description",
        status="pending",
        priority="high",
        user=other_user
    )


@pytest.mark.django_db
class TestTaskViewSet:
    def test_list_tasks(self, authenticated_client, task, other_user_task):
        """Test obtener lista de tareas del usuario"""
        url = reverse('task-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == task.title

    def test_create_task(self, authenticated_client, user):
        """Test crear una nueva tarea"""
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'status': 'pending',
            'priority': 'high'
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.count() == 1
        assert Task.objects.first().user == user

    def test_retrieve_task(self, authenticated_client, task):
        """Test obtener una tarea específica"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == task.title

    def test_update_task(self, authenticated_client, task):
        """Test actualizar una tarea"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'status': 'in_progress',
            'priority': 'high'
        }

        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Task'
        assert task.status == 'in_progress'

    def test_partial_update_task(self, authenticated_client, task):
        """Test actualización parcial de una tarea"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {'title': 'Updated Title Only'}

        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Title Only'
        assert task.status == 'pending'

    def test_delete_task(self, authenticated_client, task):
        """Test eliminar una tarea"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_complete_task(self, authenticated_client, task):
        """Test marcar una tarea como completada"""
        url = reverse('task-complete', kwargs={'pk': task.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'completed'
        assert task.completed_at is not None

    def test_reopen_task(self, authenticated_client, task):
        """Test reabrir una tarea completada"""
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()

        url = reverse('task-reopen', kwargs={'pk': task.pk})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'pending'
        assert task.completed_at is None

    def test_unauthorized_access(self, api_client, task):
        """Test acceso no autorizado"""
        url = reverse('task-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_other_user_task(self, authenticated_client, other_user_task):
        """Test intentar acceder a una tarea de otro usuario"""
        url = reverse('task-detail', kwargs={'pk': other_user_task.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('filter_param, filter_value, expected_count', [
        ('status', 'pending', 1),
        ('priority', 'high', 1),
        ('title', 'Test', 1),
        ('description', 'Test', 1),
    ])
    def test_filter_tasks(self, authenticated_client, user, filter_param, filter_value, expected_count):
        """Test filtrado de tareas"""
        Task.objects.create(
            title="Test Task 1",
            description="Test Description",
            status="pending",
            priority="medium",
            user=user
        )
        Task.objects.create(
            title="Another Task",
            description="Another Description",
            status="in_progress",
            priority="high",
            user=user
        )

        url = reverse('task-list')
        response = authenticated_client.get(url, {filter_param: filter_value})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == expected_count

    def test_multiple_filters(self, authenticated_client, user):
        """Test múltiples filtros combinados"""
        Task.objects.create(
            title="High Priority Task",
            description="Test Description",
            status="pending",
            priority="high",
            user=user
        )
        Task.objects.create(
            title="Low Priority Task",
            description="Test Description",
            status="pending",
            priority="low",
            user=user
        )

        url = reverse('task-list')
        response = authenticated_client.get(url, {
            'status': 'pending',
            'priority': 'high'
        })

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == "High Priority Task"

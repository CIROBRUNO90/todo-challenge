import pytest

from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from tasks.models import Task
from users.models import Users


@pytest.fixture
def user():
    return Users.objects.create(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def sample_task(user):
    return Task.objects.create(
        title="Test Task",
        description="Test Description",
        status="pending",
        priority="medium",
        user=user
    )


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self, user):
        """Test creación básica de una tarea"""
        task = Task.objects.create(
            title="Nueva Tarea",
            description="Descripción de prueba",
            user=user
        )
        assert task.title == "Nueva Tarea"
        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.user == user

    def test_task_str_method(self, sample_task):
        """Test método __str__ del modelo"""
        expected_str = f"{sample_task.title} - {sample_task.status}"
        assert str(sample_task) == expected_str

    def test_task_status_choices(self, user):
        """Test status solo acepta valores válidos"""
        task = Task.objects.create(
            title="Test Status",
            user=user,
            status="in_progress"
        )
        assert task.status == "in_progress"

        with pytest.raises(ValidationError):
            task = Task.objects.create(
                title="Test Invalid Status",
                user=user,
                status="invalid_status"
            )
            task.full_clean()

    def test_task_priority_choices(self, user):
        """Test prioridad solo acepta valores válidos"""
        task = Task.objects.create(
            title="Test Priority",
            user=user,
            priority="high"
        )
        assert task.priority == "high"

        with pytest.raises(ValidationError):
            task = Task.objects.create(
                title="Test Invalid Priority",
                user=user,
                priority="invalid"
            )
            task.full_clean()

    def test_task_dates(self, user):
        """Test campos de fecha"""
        task = Task.objects.create(
            title="Test Dates",
            user=user
        )
        assert task.created_at is not None
        assert task.updated_at is not None

        original_updated_at = task.updated_at
        task.title = "Updated Title"
        task.save()
        assert task.updated_at > original_updated_at

    def test_task_due_date(self, user):
        """Test campo due_date"""
        future_date = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            title="Test Due Date",
            user=user,
            due_date=future_date
        )
        assert task.due_date == future_date

    def test_task_completed_at(self, user):
        """Test campo completed_at cuando se completa una tarea"""
        task = Task.objects.create(
            title="Test Completion",
            user=user
        )
        completion_time = timezone.now()
        task.status = "completed"
        task.completed_at = completion_time
        task.save()

        assert task.completed_at == completion_time
        assert task.status == "completed"

    def test_task_user_deletion(self, sample_task, user):
        """Test tareas se eliminan cuando se elimina el usuario"""
        task_id = sample_task.id
        user.delete()
        with pytest.raises(Task.DoesNotExist):
            Task.objects.get(id=task_id)

    def test_task_ordering(self, user):
        """Test ordenamiento de las tareas por created_at"""
        task1 = Task.objects.create(title="Task 1", user=user)
        task2 = Task.objects.create(title="Task 2", user=user)
        task3 = Task.objects.create(title="Task 3", user=user)

        tasks = Task.objects.all()
        assert tasks[0] == task3
        assert tasks[1] == task2
        assert tasks[2] == task1

    def test_task_description_blank(self, user):
        """Test description puede estar vacío"""
        task = Task.objects.create(
            title="Test Blank Description",
            user=user,
            description=""
        )
        assert task.description == ""

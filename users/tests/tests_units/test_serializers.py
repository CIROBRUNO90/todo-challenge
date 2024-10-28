import pytest

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from users.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer
)


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'phone_number': '1234567890',
        'password': 'securepass123'
    }


@pytest.fixture
@pytest.mark.django_db
def created_user(user_data):
    User = get_user_model()
    return User.objects.create_user(**user_data)


@pytest.mark.django_db
class TestUserSerializer:
    def test_contains_expected_fields(self, created_user):
        """Test verifica que el serializer contiene los campos esperados"""
        serializer = UserSerializer(created_user)
        assert set(serializer.data.keys()) == {
            'id',
            'username',
            'email',
            'phone_number'
        }

    def test_serialized_data(self, created_user):
        """Test verifica la correcta serialización de datos"""
        serializer = UserSerializer(created_user)
        assert serializer.data['username'] == created_user.username
        assert serializer.data['email'] == created_user.email
        assert serializer.data['phone_number'] == created_user.phone_number


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    def test_serialize_valid_data(self, user_data):
        """Test verifica la serialización de datos válidos"""
        serializer = UserRegistrationSerializer(data=user_data)
        assert serializer.is_valid()

    def test_create_user(self, user_data):
        """Test verifica la creación de usuario a través del serializer"""
        serializer = UserRegistrationSerializer(data=user_data)
        assert serializer.is_valid()
        user = serializer.save()

        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.phone_number == user_data['phone_number']
        assert user.check_password(user_data['password'])

    def test_password_write_only(self, user_data):
        """Test verifica que el campo password es write_only"""
        serializer = UserRegistrationSerializer(data=user_data)
        assert serializer.is_valid()
        user = serializer.save()
        serialized_user = UserRegistrationSerializer(user)
        assert 'password' not in serialized_user.data

    @pytest.mark.parametrize('field', ['username', 'email', 'password'])
    def test_required_fields(self, user_data, field):
        """Test verifica campos requeridos"""
        user_data.pop(field)
        serializer = UserRegistrationSerializer(data=user_data)
        assert not serializer.is_valid()
        assert field in serializer.errors

    def test_duplicate_email(self, user_data, created_user):
        """
        Test verifica que no se pueden crear usuarios
        con email duplicado
        """
        serializer = UserRegistrationSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_invalid_email_format(self, user_data):
        """Test verifica la validación del formato de email"""
        user_data['email'] = 'invalid-email'
        serializer = UserRegistrationSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
class TestLoginSerializer:
    def test_valid_credentials(self, user_data, created_user):
        """Test verifica la validación de credenciales correctas"""
        login_data = {
            'username': user_data['email'],
            'password': user_data['password']
        }
        serializer = LoginSerializer(data=login_data)
        assert serializer.is_valid()
        validated_user = serializer.validated_data
        assert validated_user == created_user

    def test_invalid_password(self, user_data, created_user):
        """Test verifica el rechazo de contraseña incorrecta"""
        login_data = {
            'username': user_data['email'],
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=login_data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_username(self, user_data, created_user):
        """Test verifica el rechazo de usuario inexistente"""
        login_data = {
            'username': 'nonexistentuser',
            'password': user_data['password']
        }
        serializer = LoginSerializer(data=login_data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    @pytest.mark.parametrize('field', ['username', 'password'])
    def test_required_login_fields(self, field):
        """Test verifica campos requeridos para login"""
        login_data = {
            'username': 'testuser@test.com',
            'password': 'testpass'
        }
        login_data.pop(field)
        serializer = LoginSerializer(data=login_data)
        assert not serializer.is_valid()
        assert field in serializer.errors

    def test_inactive_user(self, user_data, created_user):
        """Test verifica el rechazo de usuario inactivo"""
        created_user.is_active = False
        created_user.save()

        login_data = {
            'username': user_data['email'],
            'password': user_data['password']
        }
        serializer = LoginSerializer(data=login_data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepass123',
        'phone_number': '1234567890'
    }


@pytest.fixture
@pytest.mark.django_db
def authenticated_client(api_client, user_data):
    """Cliente autenticado con un usuario y sus tokens"""
    user = User.objects.create_user(**user_data)
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, user, str(refresh)


@pytest.mark.django_db
class TestRegisterView:
    def test_successful_registration(self, api_client, user_data):
        """Test registro exitoso de usuario"""
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'refresh' in response.data
        assert 'access' in response.data
        assert response.data['user']['email'] == user_data['email']
        assert User.objects.filter(email=user_data['email']).exists()

    def test_register_duplicate_email(self, api_client, user_data):
        """Test intento de registro con email duplicado"""
        User.objects.create_user(**user_data)
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    @pytest.mark.parametrize('field', ['username', 'email', 'password'])
    def test_register_missing_required_field(self, api_client, user_data, field):
        """Test registro con campos requeridos faltantes"""
        url = reverse('register')
        data = user_data.copy()
        data.pop(field)
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert field in response.data

    def test_register_invalid_email(self, api_client, user_data):
        """Test registro con email inválido"""
        url = reverse('register')
        user_data['email'] = 'invalid-email'
        response = api_client.post(url, user_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.django_db
class TestLoginView:
    def test_successful_login(self, api_client, user_data):
        """Test login exitoso"""
        User.objects.create_user(**user_data)
        url = reverse('login')
        login_data = {
            'username': user_data['email'],
            'password': user_data['password']
        }
        response = api_client.post(url, login_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'refresh' in response.data
        assert 'access' in response.data
        assert response.data['user']['email'] == user_data['email']

    def test_login_wrong_password(self, api_client, user_data):
        """Test login con contraseña incorrecta"""
        User.objects.create_user(**user_data)
        url = reverse('login')
        login_data = {
            'username': user_data['email'],
            'password': 'wrongpassword'
        }
        response = api_client.post(url, login_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, api_client):
        """Test login con usuario inexistente"""
        url = reverse('login')
        login_data = {
            'username': 'nonexistent@test.com',
            'password': 'password123'
        }
        response = api_client.post(url, login_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self, api_client, user_data):
        """Test login con usuario inactivo"""
        user = User.objects.create_user(**user_data)
        user.is_active = False
        user.save()

        url = reverse('login')
        login_data = {
            'username': user_data['email'],
            'password': user_data['password']
        }
        response = api_client.post(url, login_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutView:
    def test_successful_logout(self, authenticated_client):
        """Test logout exitoso"""
        client, user, refresh_token = authenticated_client
        url = reverse('logout')
        response = client.post(url, {'refresh': refresh_token}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['detail'] == "Successfully logged out"

    def test_logout_without_token(self, authenticated_client):
        """Test logout sin token de refresco"""
        client, _, _ = authenticated_client
        url = reverse('logout')
        response = client.post(url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_logout_invalid_token(self, authenticated_client):
        """Test logout con token inválido"""
        client, _, _ = authenticated_client
        url = reverse('logout')
        response = client.post(
            url,
            {'refresh': 'invalid-token'},
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_logout_unauthorized(self, api_client):
        """Test intento de logout sin autenticación"""
        url = reverse('logout')
        response = api_client.post(
            url,
            {'refresh': 'some-token'},
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_twice_same_token(self, authenticated_client):
        """Test intento de logout dos veces con el mismo token"""
        client, _, refresh_token = authenticated_client
        url = reverse('logout')

        response1 = client.post(url, {'refresh': refresh_token}, format='json')
        assert response1.status_code == status.HTTP_200_OK

        response2 = client.post(url, {'refresh': refresh_token}, format='json')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

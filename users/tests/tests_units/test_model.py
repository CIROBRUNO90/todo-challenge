import pytest

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def valid_user_data():
    return {
        'email': 'test@test.com',
        'username': 'testuser',
        'phone_number': '1234567890',
        'password': 'securepass123'
    }


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_success(self, valid_user_data):
        """Test crear usuario con datos válidos"""
        user = User.objects.create_user(**valid_user_data)
        assert user.email == valid_user_data['email']
        assert user.username == valid_user_data['username']
        assert user.phone_number == valid_user_data['phone_number']
        assert user.check_password(valid_user_data['password'])

    def test_create_user_invalid_email(self, valid_user_data):
        """Test verifica la validación de email inválido"""
        valid_user_data['email'] = 'invalid_email'
        user = User(**valid_user_data)
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_user_str_method(self, valid_user_data):
        """Test verifica el método __str__"""
        user = User.objects.create_user(**valid_user_data)
        assert str(user) == valid_user_data['email']

    def test_custom_user_fields(self, valid_user_data):
        """Test verifica los campos personalizados del modelo"""
        user = User.objects.create_user(**valid_user_data)
        assert hasattr(user, 'email')
        assert hasattr(user, 'phone_number')
        assert user.USERNAME_FIELD == 'email'
        assert 'username' in user.REQUIRED_FIELDS

    @pytest.mark.parametrize('email,is_valid', [
        ('test@example.com', True),
        ('test.name@example.co.uk', True),
        ('test@.com', False),
        ('test@com', False),
        ('', False),
    ])
    def test_email_validation(self, valid_user_data, email, is_valid):
        """Test verifica diferentes formatos de email"""
        valid_user_data['email'] = email
        user = User(**valid_user_data)

        if is_valid:
            user.full_clean()
        else:
            with pytest.raises(ValidationError):
                user.full_clean()

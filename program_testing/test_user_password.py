import pytest
from features.user import User

pytestmark = pytest.mark.usefixtures("clean_user_registry")


class TestUserPassword:
    """Tests for password management."""

    def test_password_hashing(self):
        """Test password hashing and verification."""

        plain_password = '29.September.2006'
        hashed = User._hash_password(plain_password)
        assert hashed.startswith('$2b$')

        assert User._check_password(plain_password, hashed) is True
        assert User._check_password('WrongTest', hashed) is False

    def test_password_property(self, sample_user: User):
        """Test password property getter."""

        user = sample_user
        assert user.password.startswith('$2b$')

    def test_password_property_valid(self, sample_user: User):
        """Test password property setter with valid password."""

        user = sample_user
        original_hash = user.password

        user.password = '29.November.2006'
        assert user.password != original_hash
        assert user.password.startswith('$2b$')

    def test_password_property_invalid(self, sample_user: User):
        """Test password property setter with invalid password."""

        user = sample_user
        current_hash = user.password

        user.password = 'wrongPass'
        assert user.password == current_hash
import pytest
from constants.configs import VALID_PASSWORD
from features.user import User
import re

pytestmark = pytest.mark.usefixtures("clean_user_registry")


class TestUserRegistration:
    """Tests for user registration."""

    def test_successful_registration(self):
        """Test successful user registration."""

        first_reg = User.register('mrBean29', 'misterBean29./')
        assert first_reg == 1

        second_reg = User.register('mrBean29', 'misterBean29./')
        assert second_reg is None

    def test_registration_pass_same_as_username(self):
        """Test registration where password contains username."""

        result = User.register('jessica29', 'jessica29Gun./')
        assert result is None

    def test_registration_with_weak_pass(self):
        """Test registration with weak password."""

        weak_pass = ['weak', '12345678', 'password', 'abcde']

        for _pass in weak_pass:
            result = User.register('jessica29', _pass)
            assert result is None

class TestUserAuthentication:
    """Tests for user authentication (login/logout)."""

    def test_successful_login(self):
        """Test successful user login."""

        User.register('jessica29', '29.September.2006')

        result = User.login('jessica29', '29.September.2006')
        assert result == 1
        assert User.current_user is not None
        assert User.current_user.username == 'jessica29'

    def test_login_user_not_found(self):
        """Test login with non-existent user."""

        result = User.login('bolstar32', 'BolstarGans32./')
        assert result is None

    def test_login_with_wrong_password(self):
        """Test login with wrong password."""

        User.register('victorFrank32', 'strongVictory32/')
        result = User.login('victorFrank32', 'strongVictory32')
        assert result is None

    def test_user_logout(self):
        """Test user logout functionality."""

        User.register('johanLiebert12', 'johanLie32./')
        assert User.current_user is not None

        result = User._logout()
        assert result is False
        assert User.current_user is None

class TestUserEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_case_insensitive_username(self):
        """Test that usernames are handled case-insensitively."""

        User.register('JellyBean44', 'helloKitty32/')
        assert 'jellybean44'.casefold() in User.users
        assert 'JELLYBEAN44'.casefold() in User.users
        assert 'JellyBean44'.casefold() in User.users

        first_login = User.login('jellybean44', 'helloKitty32/')
        assert first_login == 1

        User._logout()
        second_login = User.login('JELLYBEAN44', 'helloKitty32/')
        assert second_login == 1

    def test_multiple_users_registration(self):
        """Test registration of multiple users."""

        User.register('Jess2Jes', 'JeCloud22./')
        User.register('SelenaGoals22', 'SeleneAids32./')
        User.register('DevinOwl32', 'ChristmasV.32')

        assert len(User.users) == 3
        assert 'Jess2Jes'.casefold() in User.users
        assert 'SelenaGoals22'.casefold() in User.users
        assert 'DevinOwl32'.casefold() in User.users
        assert User.current_user.username == 'DevinOwl32'

    def test_password_validation_regex(self):
        """Test password validation regex pattern."""

        pattern = re.compile(VALID_PASSWORD)

        valid_passwords = [
            "Password123!",
            "Test@1234",
            "HelloWorld#1",
            "Abcdefg1@",
            "P@ssw0rd"
        ]

        for password in valid_passwords:
            # use fullmatch to ensure the whole password matches the VALID_PASSWORD pattern
            assert pattern.fullmatch(password) is not None, f"Should be valid: {password}"

        invalid_passwords = [
            "weak",
            "password",
            "PASSWORD123",
            "Password",
            "12345678",
            "pass word1!",
        ]

        for password in invalid_passwords:
            assert pattern.fullmatch(password) is None, f"Should be invalid: {password}"
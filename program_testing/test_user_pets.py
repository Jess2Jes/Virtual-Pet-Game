import pytest
from features.user import User

pytestmark = pytest.mark.usefixtures("clean_user_registry")


class TestUserPets:
    """Tests for pet management."""

    def test_add_pet(self, sample_user: User, mock_pet):
        """Test adding a pet to user."""
        user = sample_user
        pet = mock_pet

        assert len(user.pets) == 0
        user.add_pet(pet)
        assert len(user.pets) == 1
        assert user.pets[0] is pet
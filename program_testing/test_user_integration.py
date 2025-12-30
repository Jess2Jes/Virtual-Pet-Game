import pytest
from features.user import User

pytestmark = pytest.mark.usefixtures("clean_user_registry")


class TestUserIntegration:
    """Integration tests for User class."""

    def test_complete_user_flow(self, mock_pet):
        """Test a complete user flow: register, modify, save, restore."""

        result = User.register('jessica29', '29.September.2006')
        assert result == 1
        user = User.current_user

        user.currency = 5000
        user.add_item('food', 'Mozarella Nugget', 5)
        user.add_item('food', 'Mashed Potato', 3)

        pet = mock_pet
        pet.name = 'Dugong'
        pet.type = 'Dragon'
        user.add_pet(pet)

        memento = user.create_memento()

        new_user = User('jessica29', '29.September.2006')
        new_user.restore_from_memento(memento)

        assert new_user.username == 'jessica29'
        assert new_user.currency == 5000
        assert new_user.inventory['food']['Mozarella Nugget'] == 8
        assert new_user.inventory['food']['Mashed Potato'] == 6
        assert len(new_user.pets) == 1
        assert new_user.pets[0].name == 'Dugong'
        assert new_user.pets[0].type == 'Dragon'

    def test_multiple_users_isolation(self):
        """Test that multiple users have isolated data."""

        first_user = User('HotmanPars21', 'HotDoggie.32!')
        first_user.currency = 1000
        first_user.add_item('food', 'Mozarella Nugget', 10)

        second_user = User('TofuRegex22', 'smartTofu78!')
        second_user.currency = 2000
        second_user.add_item('food', 'French Fries', 8)

        assert first_user.currency == 1000
        assert second_user.currency == 2000

        assert first_user.inventory['food']['Mozarella Nugget'] == 13
        assert second_user.inventory['food']['Mozarella Nugget'] == 3

        assert first_user.inventory['food']['French Fries'] == 3
        assert second_user.inventory['food']['French Fries'] == 11
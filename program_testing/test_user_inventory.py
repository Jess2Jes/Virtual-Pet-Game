import pytest
from features.user import User
from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF, FAT_BURNER

pytestmark = pytest.mark.usefixtures("clean_user_registry")


class TestUserInventory:
    """Tests for inventory management."""

    def test_inventory_default_values(self, sample_user: User):
        """Test that inventory is initialized with correct default values."""

        user = sample_user

        for food_item in FOOD_DEF:
            assert user.inventory['food'][food_item] == 3

        for soap_item in SOAP_DEF:
            assert user.inventory['soap'][soap_item] == 3

        for potion_item in POTION_DEF:
            assert user.inventory['potion'][potion_item] == 3

    def test_add_item(self, sample_user: User):
        """Test adding items to inventory."""

        user = sample_user

        initial_food_count = user.inventory['food']['Mozarella Nugget']
        user.add_item('food', 'Mozarella Nugget', 2)
        assert user.inventory['food']['Mozarella Nugget'] == initial_food_count + 2

        initial_soap_count = user.inventory['soap']['Rainbow Bubble Soap']
        user.add_item('soap', 'Rainbow Bubble Soap', 3)
        assert user.inventory['soap']['Rainbow Bubble Soap'] == initial_soap_count + 3

        initial_potion_count = user.inventory['potion'][FAT_BURNER]
        user.add_item('potion', FAT_BURNER, 2)
        assert user.inventory['potion'][FAT_BURNER] == initial_potion_count + 2

    def test_has_item(self, sample_user: User):
        """Test checking item availability."""

        user = sample_user
        assert user.has_item('food', 'Mozarella Nugget', 1) is True
        assert user.has_item('food', 'Mozarella Nugget', 100) is False

        assert user.has_item('something', 'item', 1) is False
        assert user.has_item('soap', 'Matcha Soap', 1) is False

    def test_consume_item(self, sample_user: User):
        """Test consuming items from inventory."""

        user = sample_user
        initial_count = user.inventory['food']['Mozarella Nugget']
        result = user.consume_item('food', 'Mozarella Nugget', 2)
        assert result is True
        assert user.inventory['food']['Mozarella Nugget'] == initial_count - 2

        result = user.consume_item('food', 'Fried Rice', 100)
        assert result is False
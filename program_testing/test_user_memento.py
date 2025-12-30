import pytest
from features.user import User
import bcrypt
from constants.configs import FAT_BURNER

pytestmark = pytest.mark.usefixtures("clean_user_registry")


class TestUserMemento:
    """Tests for memento (save/restore) functionality."""

    def test_create_memento(self, sample_user_with_pet: User):
        """Test creating a memento (save state)."""

        user = sample_user_with_pet
        memento = user.create_memento()

        assert memento['username'] == 'jessica29'
        assert memento['password'] == user.password

        assert set(['currency', 'inventory', 'music', 'food', 'pets']).issubset(memento.keys())

        assert len(memento['pets']) == 1
        assert memento['pets'][0]['name'] == 'WeeWee'
        assert memento['pets'][0]['type'] == 'Cat'

    def test_restore_from_memento(self, sample_user: User):
        """Test restoring user state from memento."""

        user = sample_user

        memento = {
            "username": "jessica29",
            "password": bcrypt.hashpw(
                "29.September.2006".encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8'),
            "currency": 5000,
            "inventory": {
                "food": {
                    "Mozarella Nugget": 10,
                    "Ice Cream": 5,
                    "Fried Rice": 4
                },
                "soap": {
                    "Rainbow Bubble Soap": 5
                },
                "potion": {
                    FAT_BURNER: 2
                }
            },
            "music": {"Night Changes"},
            "food": {"Pizza"},
            "pets": [{
                "name": "WeeWee",
                "type": "Cat",
                "age": 2.0,
                "happiness": 90,
                "hunger": 20,
                "sanity": 85,
                "health": 95,
                "fat": 5,
                "energy": 80,
                "generosity": 2
            }]
        }

        user.restore_from_memento(memento)

        assert user.username == 'jessica29'
        assert user.currency == 5000
        assert user.inventory['food']['Ice Cream'] == 5
        assert user.music == {'Night Changes'}
        assert user.food == {'Pizza'}
        assert len(user.pets) == 1
        assert user.pets[0].name == 'WeeWee'
        assert user.pets[0].type == 'Cat'
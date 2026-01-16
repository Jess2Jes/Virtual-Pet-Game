from features.user import User

"""
program_testing/test_user_memento.py

Unit tests for the Memento pattern implementation in the User class.

This module verifies that the User entity can be:
1. Serialized into a dictionary snapshot (memento) suitable for JSON storage.
2. Restored from a dictionary snapshot, including the reconstruction of complex dependencies like Pet objects.

"""

class TestUserMemento:
    """
    Test suite for User state persistence.
    
    Focuses on:
    - create_memento(): Capturing state.
    - restore_from_memento(): Re-applying state.
    """

    def test_create_memento(self, user: User):
        """
        Test creating a state snapshot (memento) from a User instance.
        
        Ensures that:
        - Primitive fields (currency, username) are captured correctly.
        - Complex nested objects (pets) are serialized into dictionaries.
        """

        user.currency = 2500
        pet = user.pet_factory.create('Cat', 'Poodle', 1.5)
        user.add_pet(pet)
        assert len(user.pets) != 0
        memento = user.create_memento()
        assert memento['username'] == 'jessica29'
        assert memento['currency'] == 2500
        assert len(memento['pets']) == 1
        assert memento['pets'][0]['name'] == 'Poodle'
    
    def test_restore_from_memento(self, user: User):
        """
        Test restoring a User's state from a memento dictionary.
        
        Verifies that:
        - User properties (currency, username) are updated from the dict.
        - Pets are correctly recreated using the injected PetFactory.
        - Pet statistics (health, happiness, hunger, etc.) are restored exactly as saved.
        """

        last_memento = {
            'username': user.username,
            'password': user.password,
            'currency': 10000000,
            'inventory': user.inventory,
            'music': user.music,
            'food': user.food,
            'pets': [
                {
                    "name": 'Poodle',
                    "type": 'Cat',
                    "age": 1.5,
                    "happiness": 80,
                    "hunger": 50,
                    "sanity": 50,
                    "health": 50,
                    "fat": 20,
                    "energy": 50,
                    "generosity": 0,
                },
                {
                    "name": 'Toothless',
                    "type": 'Dragon',
                    "age": 100,
                    "happiness": 80,
                    "hunger": 50,
                    "sanity": 50,
                    "health": 35,
                    "fat": 20,
                    "energy": 20,
                    "generosity": 0,
                },
            ]
        }
        user.restore_from_memento(last_memento)

        assert user.username == 'jessica29'
        assert user.currency == 10000000
        assert len(user.pets) == 2
        restored_pets = user.pets

        for pet in restored_pets:
            assert pet.name in ['Poodle', 'Toothless']
            assert pet.age in [1.5, 100]
            assert pet.happiness == 80
            assert pet.hunger == 50
            assert pet.sanity == 50
            assert pet.health in [35, 50]
            assert pet.fat == 20
            assert pet.energy in [20, 50]
            assert pet.generosity == 0
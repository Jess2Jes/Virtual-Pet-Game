import pytest
import sys
from pathlib import Path
from typing import Generator
from features.user import User

repo_root = Path(__file__).resolve().parent.parent
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)


class MockPet:
    """Simple mock pet class for testing."""

    def __init__(self, name: str = 'WeeWee', species: str = 'Cat', age: float = 1.0):
        self.name = name
        self.type = species
        self.age = age
        self.happiness = 80
        self.hunger = 30
        self.sanity = 90
        self.health = 95
        self.fat = 0
        self.energy = 85
        self.generosity = 0

@pytest.fixture
def mock_pet() -> MockPet:
    """Fixture to create a mock pet."""
    return MockPet()

@pytest.fixture(autouse=True)
def clean_user_registry() -> Generator[None, None, None]:
    """
    Fixture to clear user registry before each test.
    autouse=True ensures it runs for every test automatically.
    """
    User.users.clear()
    User.current_user = None
    yield
    # After a test, ensure registry is still clean (defensive).
    User.users.clear()
    User.current_user = None

@pytest.fixture
def sample_user() -> User:
    """Fixture to create a sample user for testing."""
    return User('jessica29', '29.September.2006')

@pytest.fixture
def sample_user_with_pet() -> User:
    """Fixture to create a user with a pet."""
    user = User('jessica29', '29.September.2006')
    pet = MockPet()
    user.add_pet(pet)
    return user

@pytest.fixture
def registered_user() -> User:
    """Fixture to register a user in the system and return current_user."""
    User.register('jessica29', '29.September.2006')
    return User.current_user
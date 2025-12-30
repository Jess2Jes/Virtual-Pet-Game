import sys
from pathlib import Path
from typing import Generator, Optional

import pytest

def find_repo_root_with_features(max_levels: int = 6) -> Optional[Path]:
    cur = Path(__file__).resolve().parent
    for _ in range(max_levels):
        if (cur / "features").is_dir():
            return cur
        cur = cur.parent
    return None

_repo_root = find_repo_root_with_features()
if _repo_root is None:
    _repo_root = Path(__file__).resolve().parent.parent

_repo_root_str = str(_repo_root)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

try:
    from features.user import User
except Exception as exc:
    raise ImportError(
        "Could not import 'features.user'. Make sure there is a 'features' package "
        f"directory at or above {Path(__file__).resolve().parent} and that you run "
        "pytest from the repository (or set PYTHONPATH). Original error: "
        f"{exc!s}"
    ) from exc

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
    """Fixture that returns a lightweight mock pet instance."""
    return MockPet()

@pytest.fixture(autouse=True)
def clean_user_registry() -> Generator[None, None, None]:
    """Autouse fixture to clear User registry before and after each test."""
    User.users.clear()
    User.current_user = None
    yield
    User.users.clear()
    User.current_user = None

@pytest.fixture
def sample_user() -> User:
    """Fixture to create a sample user for testing."""
    return User('jessica29', '29.September.2006')

@pytest.fixture
def sample_user_with_pet() -> User:
    """Fixture to create a sample user prepopulated with a pet."""
    user = User('jessica29', '29.September.2006')
    pet = MockPet()
    user.add_pet(pet)
    return user

@pytest.fixture
def registered_user() -> User:
    """Fixture to register a user in the system and return current_user."""
    User.register('jessica29', '29.September.2006')
    return User.current_user
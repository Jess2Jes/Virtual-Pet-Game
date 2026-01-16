import pytest
from features.user import User, BcryptAuthService, DefaultPetFactory

"""
program_testing/conftest.py

Shared fixtures for the program_testing test suite.

This module contains common setup code used across multiple test files,
specifically for creating User instances with real dependencies (BcryptAuthService, DefaultPetFactory)
to ensure integration tests run against a realistic object graph.
"""

@pytest.fixture
def user():
    """
    Pytest fixture that provides a fresh User instance for each test.

    This user is initialized with:
    - A default username ('jessica29').
    - A concrete BcryptAuthService for real password hashing/verification.
    - A concrete DefaultPetFactory for creating pet objects.

    Returns:
        User: A fully initialized User object ready for testing.
    """

    return User(
        username='jessica29', 
        auth_service=BcryptAuthService(),
        pet_factory=DefaultPetFactory()
    )
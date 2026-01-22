"""
features/user.py

User domain model with injectable authentication and pet restoration collaborators.

This file preserves the original public API and behavior while improving SRP/DIP:
- Authentication hashing/verification is delegated to an AuthService.
- Pet restoration is delegated to a PetFactory that can use a builder to satisfy IO requirements.
"""

import re
import bcrypt
from typing import Dict, Any, Protocol
from random import randrange

from constants.configs import (
    AuthConfig as AC,
    PotionConfig as PC,
    FoodConfig as FC,
    SoapConfig as SC
    )
from utils.ports import OutputPort
from features.pet_construction import DefaultPetBuilder, PetBuilder


class AuthService(Protocol):
    """Authentication service abstraction used by the User entity."""
    def hash(self, password: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...


class BcryptAuthService:
    """Concrete AuthService using bcrypt."""
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


class PetFactory(Protocol):
    """Factory abstraction for restoring pets from saved mementos."""
    def create(self, pet_type: str, name: str, age: float, io: OutputPort | None = None): ...


class DefaultPetFactory:
    """
    Default pet factory mapping saved types to concrete pet classes.

    Collaboration:
    - Uses a `PetBuilder` to ensure restored pets always get an OutputPort.
    - Preserves the existing create() API used by User.restore_from_memento().
    """

    def __init__(self, builder: PetBuilder | None = None, default_io: OutputPort | None = None):
        self._builder = builder or DefaultPetBuilder(default_io=default_io)

    def create(self, pet_type: str, name: str, age: float, io: OutputPort | None = None):
        # Preserve the old create() signature and behavior expectations.
        return self._builder.create(pet_type, name, age, io)


class User:
    """
    Represents a player/account.

    Collaboration:
    - Owns pets, inventory, currency, and preference capture (music/food dicts).
    - Delegates password hashing/verification to an AuthService.
    - Delegates pet restoration to a PetFactory.
    """

    def __init__(
        self,
        username: str,
        password_hash: str = "",
        auth_service: AuthService | None = None,
        pet_factory: PetFactory | None = None,
    ):
        self.auth_service = auth_service or BcryptAuthService()
        self.pet_factory = pet_factory or DefaultPetFactory()
        self.username = username
        self.__password_hash = password_hash
        self.pets: list = []
        self.music: Dict[str, Any] = {}
        self.food: Dict[str, Any] = {}
        self._currency: int = randrange(0, 25000)

        self.inventory: Dict[str, Dict[str, int]] = {
            "food": dict.fromkeys(FC.DEFINITIONS.keys(), 3),
            "soap": dict.fromkeys(SC.DEFINITIONS.keys(), 3),
            "potion": dict.fromkeys(PC.DEFINITIONS.keys(), 3),
        }

    @property
    def currency(self) -> int:
        return self._currency

    @currency.setter
    def currency(self, value) -> None:
        if value < 0:
            raise ValueError("Currency cannot be negative.")
        self._currency = value

    def limit_currency(self) -> None:
        val = int(getattr(self, "currency"))
        setattr(self, "currency", max(0, min(2_147_483_647, val)))

    @property
    def password(self) -> str:
        return self.__password_hash

    @password.setter
    def password(self, new_password: str):
        if not re.match(AC.VALID_PASSWORD, new_password):
            raise ValueError(
                "Password is too weak! Must contain 8+ chars, 1 upper, 1 lower, 1 digit, 1 symbol."
            )
        self.__password_hash = self.auth_service.hash(new_password)

    def add_pet(self, pet) -> None:
        """Attach a new pet to the user."""
        self.pets.append(pet)

    def add_item(self, category: str, name: str, amount: int) -> None:
        """Add quantity of an inventory item."""
        if category in self.inventory and name in self.inventory[category]:
            self.inventory[category][name] += int(amount)

    def has_item(self, category: str, name: str, amount: int = 1) -> bool:
        """Return True if the user has at least `amount` of the given item."""
        return (
            category in self.inventory
            and name in self.inventory[category]
            and self.inventory[category][name] >= amount
        )

    def consume_item(self, category: str, name: str, amount: int = 1) -> bool:
        """Consume an inventory item if available and return whether it succeeded."""
        if self.has_item(category, name, amount):
            self.inventory[category][name] -= amount
            return True
        return False

    def create_memento(self) -> Dict[str, Any]:
        """Create a dict snapshot of user state suitable for JSON persistence."""
        pets_data = []
        for pet in self.pets:
            pet_data = {
                "name": pet.name,
                "type": pet.type,
                "age": pet.age,
                "happiness": pet.happiness,
                "hunger": pet.hunger,
                "sanity": pet.sanity,
                "health": pet.health,
                "fat": pet.fat,
                "energy": pet.energy,
                "generosity": pet.generosity,
            }
            pets_data.append(pet_data)

        user_data = {
            "username": self.username,
            "password": self.__password_hash,
            "currency": self._currency,
            "inventory": self.inventory,
            "music": self.music,
            "food": self.food,
            "pets": pets_data,
        }

        return user_data

    def restore_from_memento(self, memento: Dict[str, Any], io: OutputPort = None) -> None:
        """
        Restore user state from a previously created memento.

        Behavior is preserved: pet stats are restored exactly as before.
        """
        self.username = memento.get("username", self.username)
        self.__password_hash = memento.get("password", self.__password_hash)
        self._currency = memento.get("currency", 0)
        self.inventory = memento.get("inventory", self.inventory)
        self.music = memento.get("music", {})
        self.food = memento.get("food", {})

        self.pets = []
        for pet_data in memento.get("pets", []):
            pet_type = pet_data.get("type", "Cat")
            pet = self.pet_factory.create(pet_type, pet_data["name"], pet_data.get("age", 0.0), io=io)

            pet.happiness = pet_data.get("happiness", 50)
            pet.hunger = pet_data.get("hunger", 50)
            pet.sanity = pet_data.get("sanity", 50)
            pet.health = pet_data.get("health", 50)
            pet.fat = pet_data.get("fat", 0)
            pet.energy = pet_data.get("energy", 50)
            pet.generosity = pet_data.get("generosity", 0)

            self.pets.append(pet)
"""User domain model with injectable auth service and pet factory for restoration.

"""

import math
import re
import bcrypt
from typing import Dict, Any, Optional, Protocol
from random import randrange
from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF, VALID_PASSWORD
from colorama import init
from utils.colorize import red, yellow, green

init(autoreset=True)


class AuthService(Protocol):
    """Authentication service abstraction."""
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
    def create(self, pet_type: str, name: str, age: float): ...


class DefaultPetFactory:
    """Default pet factory mapping saved types to concrete pet classes."""
    def __init__(self):
        from .animal import Cat, Rabbit, Dino, Dragon, Pou
        self._pet_class_map = {
            "Cat": Cat,
            "Rabbit": Rabbit,
            "Dinosaur": Dino,
            "Dragon": Dragon,
            "Pou": Pou,
        }
        self._default_cls = Cat

    def create(self, pet_type: str, name: str, age: float):
        cls = self._pet_class_map.get(pet_type, self._default_cls)
        return cls(name, age)


class User:
    """Represents a player/account with inventory, pets, and profile data."""
    users: Dict[str, "User"] = {}
    current_user: Optional["User"] = None

    def __init__(
        self,
        username: str,
        password: str,
        auth_service: AuthService | None = None,
        pet_factory: PetFactory | None = None,
    ):
        self.auth_service = auth_service or BcryptAuthService()
        self.pet_factory = pet_factory or DefaultPetFactory()
        self.username = username
        self.__password_hash = (
            self.auth_service.hash(password) if not password.startswith('$2b$') else password
        )
        self.pets: list = []
        self.music: Dict[str, Any] = {}
        self.food: Dict[str, Any] = {}
        self._currency: int = randrange(0, 25000)

        self.inventory: Dict[str, Dict[str, int]] = {
            "food": dict.fromkeys(FOOD_DEF.keys(), 3),
            "soap": dict.fromkeys(SOAP_DEF.keys(), 3),
            "potion": dict.fromkeys(POTION_DEF.keys(), 3),
        }

    @property
    def currency(self) -> int:
        return self._currency

    @currency.setter
    def currency(self, value) -> None:
        if value < 0:
            print(red("\nCurrency cannot be below 0!"))
        else:
            self._currency = value

    def limit_currency(self) -> None:
        val = int(getattr(self, "currency"))
        setattr(self, "currency", max(0, min(math.inf, val)))

    @property
    def password(self) -> str:
        return self.__password_hash

    @password.setter
    def password(self, new_password: str):
        if not re.match(VALID_PASSWORD, new_password):
            print(red("Change password operation unsuccessful!"))
            print(yellow("Password must contain:"))
            print(yellow("At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char\n"))
            return
        self.__password_hash = self.auth_service.hash(new_password)

    def add_pet(self, pet) -> None:
        self.pets.append(pet)

    def add_item(self, category: str, name: str, amount: int) -> None:
        if category in self.inventory and name in self.inventory[category]:
            self.inventory[category][name] += int(amount)

    def has_item(self, category: str, name: str, amount: int = 1) -> bool:
        return (
            category in self.inventory
            and name in self.inventory[category]
            and self.inventory[category][name] >= amount
        )

    def consume_item(self, category: str, name: str, amount: int = 1) -> bool:
        if self.has_item(category, name, amount):
            self.inventory[category][name] -= amount
            return True
        return False

    @classmethod
    def register(cls, username: str, password: str) -> Optional[int]:
        print()
        key = username.casefold()

        if key in cls.users:
            print(red("This username has already existed!\n"))
            return None
        if username.strip().lower() in password.strip().lower():
            print(red("Password cannot be the same as username!\n"))
            return None

        if not re.match(VALID_PASSWORD, password):
            print(red("Password is too weak!\n"))
            print(yellow("Password must contain:"))
            print(yellow("At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char\n"))
            return None

        new_user = cls(username, password)
        cls.users[key] = new_user
        cls.current_user = new_user
        print(green(f"User {username} registered successfully.\n"))
        return 1

    @classmethod
    def login(cls, username: str, password: str) -> Optional[int]:
        print()
        key = username.casefold()
        if key not in cls.users:
            print(red("User not found!\n"))
            return None

        user = cls.users[key]
        if not user.auth_service.verify(password, user.__password_hash):
            print(red("Wrong password!\n"))
            return None

        cls.current_user = user
        print(green(f"Welcome back, {username}!\n"))
        return 1

    @classmethod
    def _logout(cls) -> bool:
        cls.current_user = None
        print()
        return False

    def create_memento(self) -> Dict[str, Any]:
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

    def restore_from_memento(self, memento: Dict[str, Any]) -> None:
        self.username = memento.get("username", self.username)
        self.__password_hash = memento.get("password", self.__password_hash)
        self._currency = memento.get("currency", 0)
        self.inventory = memento.get("inventory", self.inventory)
        self.music = memento.get("music", {})
        self.food = memento.get("food", {})

        self.pets = []
        for pet_data in memento.get("pets", []):
            pet_type = pet_data.get("type", "Cat")
            pet = self.pet_factory.create(pet_type, pet_data["name"], pet_data.get("age", 0.0))

            pet.happiness = pet_data.get("happiness", 50)
            pet.hunger = pet_data.get("hunger", 50)
            pet.sanity = pet_data.get("sanity", 50)
            pet.health = pet_data.get("health", 50)
            pet.fat = pet_data.get("fat", 0)
            pet.energy = pet_data.get("energy", 50)
            pet.generosity = pet_data.get("generosity", 0)

            self.pets.append(pet)
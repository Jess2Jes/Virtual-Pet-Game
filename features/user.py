import math
import asyncio
import re
import bcrypt
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)
from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF
from random import randrange
from typing import Dict, Any, Optional
from colorama import init
from .pet import VirtualPet
from utils.colorize import red, yellow, green
init(autoreset=True)


"""
user.py

User model and helper utilities for the Virtual Pet Game.

Responsibilities:
- Represent users (username, hashed password, currency, inventory, pets, profile fields).
- Provide registration/login flows, password hashing/checking, and simple persistence helpers
  (create_memento / restore_from_memento) used by the memento/save system.
- Expose an async `loading()` helper used by UI flows to show a progress bar.

Notes:
- Passwords are hashed with bcrypt. When restoring from saved state the module accepts
  pre-hashed passwords (starting with the bcrypt prefix).
- Inventory is initialized from the VirtualPet class-level item definitions.
- This file includes light input validation and prints user-facing messages; core logic is unchanged.
"""

# Regular expression for strong passwords:
valid_password = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"


async def loading():
    """Async helper that displays a short progress bar (used by UI flows)."""
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn()
    )
    task = progress.add_task("Loading.. .", total=150)
    with progress:
        for _ in range(150):
            progress.update(task, advance=1)
            await asyncio.sleep(0.01)


class User:
    """
    Represents a player / account in the game.

    Attributes:
        users: class-level mapping of username -> User (in-memory registry).
        current_user: class-level pointer to the signed-in user.
    """

    users: Dict[str, "User"] = {}
    current_user: Optional["User"] = None

    def __init__(self, username: str, password: str):
        """
        Create a new User instance.

        Args:
            username: the account name.
            password: plaintext password or existing bcrypt hash (starting with $2b$).
        """
        self.username = username
        # Accept pre-hashed bcrypt strings or hash plaintext passwords
        self.__password_hash = (
            self._hash_password(password) if not password.startswith('$2b$') else password
        )
        self.pets: list = []
        self.music: Dict[str, Any] = {}
        self.food: Dict[str, Any] = {}
        self._currency: int = randrange(0, 25000)

        # Initialize inventory from VirtualPet definitions (default quantity 3)
        self.inventory: Dict[str, Dict[str, int]] = {
            "food": dict.fromkeys(FOOD_DEF.keys(), 3),
            "soap": dict.fromkeys(SOAP_DEF.keys(), 3),
            "potion": dict.fromkeys(POTION_DEF.keys(), 3),
        }

    @staticmethod
    def _hash_password(password: str) -> str:
        """Return a bcrypt hash for the given plaintext password."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _check_password(password: str, hashed: str) -> bool:
        """Verify a plaintext password against a bcrypt hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    @property
    def currency(self) -> int:
        """Current currency (int)."""
        return self._currency

    @currency.setter
    def currency(self, value) -> None:
        """Set currency ensuring it is non-negative; prints a message on invalid attempts."""
        if value < 0:
            print(red("\nCurrency cannot be below 0!"))
        else:
            self._currency = value

    def limit_currency(self) -> None:
        """
        Clamp currency to a sensible non-negative bound.

        Uses math.inf to keep the API but ensures currency is not negative.
        """
        val = int(getattr(self, "currency"))
        setattr(self, "currency", max(0, min(math.inf, val)))

    @property
    def password(self) -> str:
        """Return the stored bcrypt password hash (do not expose plaintext)."""
        return self.__password_hash

    @password.setter
    def password(self, new_password: str):
        """
        Change password after validating strength.

        The method enforces the `valid_password` regex and will print a message
        if the new password is not acceptable.
        """
        if not re.match(valid_password, new_password):
            print(red("Change password operation unsuccessful!"))
            print(yellow("Password must contain:"))
            print(yellow("At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char\n"))
            return
        self.__password_hash = self._hash_password(new_password)

    def add_pet(self, pet: VirtualPet) -> None:
        """Attach a new pet to this user's pet list."""
        self.pets.append(pet)

    def add_item(self, category: str, name: str, amount: int) -> None:
        """Increase inventory count for a given category/name by amount."""
        if category in self.inventory and name in self.inventory[category]:
            self.inventory[category][name] += int(amount)

    def has_item(self, category: str, name: str, amount: int = 1) -> bool:
        """Check whether the user has at least `amount` of a named item."""
        return (
            category in self.inventory
            and name in self.inventory[category]
            and self.inventory[category][name] >= amount
        )

    def consume_item(self, category: str, name: str, amount: int = 1) -> bool:
        """Consume (subtract) items from inventory when available; return True on success."""
        if self.has_item(category, name, amount):
            self.inventory[category][name] -= amount
            return True
        return False

    @classmethod
    def register(cls, username: str, password: str) -> Optional[int]:
        """
        Register a new user.

        Returns:
          1 on success, None on failure (and prints diagnostic messages).
        """
        print()
        if username in cls.users:
            print(red("This username has already existed!\n"))
            return None
        if username.strip().lower() in password.strip().lower():
            print(red("Password cannot be the same as username!\n"))
            return None

        if not re.match(valid_password, password):
            print(red("Password is too weak!\n"))
            print(yellow("Password must contain:"))
            print(yellow("At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char\n"))
            return None

        new_user = cls(username, password)
        cls.users[username] = new_user
        cls.current_user = new_user
        print(green(f"User {username} registered successfully.\n"))
        return 1

    @classmethod
    def login(cls, username: str, password: str) -> Optional[int]:
        """
        Authenticate a user by username and plaintext password.

        Returns:
          1 on success, None on failure.
        """
        print()
        if username not in cls.users:
            print(red("User not found!\n"))
            return None

        user = cls.users[username]
        # Access the instance's stored hash to validate credentials
        if not cls._check_password(password, user.__password_hash):
            print(red("Wrong password!\n"))
            return None

        cls.current_user = user
        print(green(f"Welcome back, {username}!\n"))
        return 1

    @classmethod
    def _logout(cls) -> bool:
        """Clear the current_user pointer (used by UI flows)."""
        cls.current_user = None
        print()
        return False

    def create_memento(self) -> Dict[str, Any]:
        """
        Produce a serializable snapshot of the user and their pets suitable for saving.

        Returns:
            A dict representing the user's state (username, hashed password, currency, inventory, profile, pets).
        """
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
        """
        Restore this user's state from a previously created memento dict.

        The function recreates pet instances based on the stored 'type' field and restores
        primitive attributes. Unknown pet types default to Cat.
        """
        from .animal import Cat, Rabbit, Dino, Dragon, Pou

        self.username = memento.get("username", self.username)
        self.__password_hash = memento.get("password", self.__password_hash)
        self._currency = memento.get("currency", 0)
        self.inventory = memento.get("inventory", self.inventory)
        self.music = memento.get("music", {})
        self.food = memento.get("food", {})

        self.pets = []
        pet_class_map = {
            "Cat": Cat,
            "Rabbit": Rabbit,
            "Dinosaur": Dino,
            "Dragon": Dragon,
            "Pou": Pou,
        }

        for pet_data in memento.get("pets", []):
            pet_type = pet_data.get("type", "Cat")
            pet_class = pet_class_map.get(pet_type, Cat)

            pet = pet_class(pet_data["name"], pet_data.get("age", 0.0))
            pet.happiness = pet_data.get("happiness", 50)
            pet.hunger = pet_data.get("hunger", 50)
            pet.sanity = pet_data.get("sanity", 50)
            pet.health = pet_data.get("health", 50)
            pet.fat = pet_data.get("fat", 0)
            pet.energy = pet_data.get("energy", 50)
            pet.generosity = pet_data.get("generosity", 0)

            self.pets.append(pet)
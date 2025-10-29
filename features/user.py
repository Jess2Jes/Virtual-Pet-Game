# user.py
from .pet import VirtualPet
import math
import string
from random import randrange
from typing import Dict
from colorama import Fore, init
init(autoreset=True)
import asyncio
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)

GARIS = "─────────────────────────────────────────────────────────────────────────────────────────────────────"

async def loading():
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn()
    )
    task = progress.add_task("Loading...", total=100)
    with progress:
        for _ in range(100):
            progress.update(task, advance=1)
            await asyncio.sleep(0.015)

class User:
    users = {}
    current_user = None

    def __init__(self, username: str, password: str):
        self.username = username
        self.__password = password
        self.pets = []
        self.music = {}
        self.food = {}
        self._currency = randrange(0, 25000)

        self.inventory: Dict[str, Dict[str, int]] = {
            "food": dict.fromkeys(VirtualPet.FOOD_DEF.keys(), 3),
            "soap": dict.fromkeys(VirtualPet.SOAP_DEF.keys(), 3),
            "potion": dict.fromkeys(VirtualPet.POTION_DEF.keys(), 3),
        }

    @property
    def currency(self) -> int:
        return self._currency

    @currency.setter
    def currency(self, value) -> None:
        if value < 0:
            print(Fore.RED + "\nCurrency cannot be below 0!")
        else:
            self._currency = value

    def limit_currency(self) -> None:
        val = int(getattr(self, "currency"))
        setattr(self, "currency", max(0, min(math.inf, val)))

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, new_password) -> None | int:
        total_digit = sum(ch.isdigit() for ch in new_password)
        total_symbol = sum(1 for ch in new_password if ch in string.punctuation)
        total_letter = sum(ch.isalpha() for ch in new_password)

        if (total_digit < 1 or total_letter < 8 or total_symbol < 2):
            print(Fore.RED + "\nChange password operation unsuccessful!")
            print(Fore.YELLOW + "(Password must contain at least 1 digit, 8 letters, and 2 symbols)")
        else:
            self.__password = new_password

    def add_pet(self, pet: VirtualPet) -> None:
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
    def register(cls, username: str, password: str) -> None | int:

        print()
        if username in cls.users:
            print(Fore.RED + "This username has already signed in!\n")
            return None
        if username.strip().lower() in password.strip().lower():
            print(Fore.RED + "Password cannot be the same as username!\n")
            return None

        total_digit = sum(ch.isdigit() for ch in password)
        total_symbol = sum(1 for ch in password if ch in string.punctuation)
        total_letter = sum(ch.isalpha() for ch in password)

        if total_digit < 1:
            print(Fore.RED + "Password must contain at least 1 digit!\n")
            print(GARIS)
            return None
        if total_symbol < 2:
            print(Fore.RED + "Password must consist of at least 2 symbols!\n")
            print(GARIS)
            return None
        if total_letter < 8:
            print(Fore.RED + "Password must consist of at least 8 letters!\n")
            print(GARIS)
            return None

        new_user = cls(username, password)
        cls.users[username] = new_user
        cls.current_user = new_user
        print(Fore.GREEN + f"User {username} registered successfully.\n")
        return 1

    @classmethod
    def login(cls, username: str, password: str) -> None | int:

        print()
        if username not in cls.users:
            print(Fore.RED + "User not found!\n")
            return None
        if cls.users[username].password != password:
            print(Fore.RED + "Wrong password!\n")
            return None

        cls.current_user = cls.users[username]
        print(Fore.GREEN + f"Welcome back, {username}!\n")
        return 1
    
    @classmethod
    def _logout(cls) -> bool:
        cls.current_user = None
        print()
        return False
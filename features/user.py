from . pet import VirtualPet
import math
from random import randrange
from typing import Dict, Any
from colorama import Fore, init
init(autoreset=True)
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

valid_password = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"
GARIS = "─" * 101

async def loading():
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
    users = {}
    current_user = None

    def __init__(self, username: str, password: str):
        self.username = username
        self.__password_hash = self._hash_password(password) if not password.startswith('$2b$') else password
        self. pets = []
        self.music = {}
        self.food = {}
        self._currency = randrange(0, 25000)

        self.inventory: Dict[str, Dict[str, int]] = {
            "food": dict. fromkeys(VirtualPet.FOOD_DEF. keys(), 3),
            "soap": dict.fromkeys(VirtualPet.SOAP_DEF.keys(), 3),
            "potion": dict.fromkeys(VirtualPet.POTION_DEF.keys(), 3),
        }

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()). decode('utf-8')
    
    @staticmethod
    def _check_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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
        return self.__password_hash

    @password.setter
    def password(self, new_password: str):
        if not re.match(valid_password, new_password):
            print(Fore.RED + "Change password operation unsuccessful!")
            print(Fore. YELLOW + "Password must contain:")
            print(Fore. YELLOW + "At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char\n")
            return
        self.__password_hash = self._hash_password(new_password)

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
        if username.strip(). lower() in password.strip().lower():
            print(Fore.RED + "Password cannot be the same as username!\n")
            return None

        if not re.match(valid_password, password):
            print(Fore.RED + "Password is too weak!\n")
            print(Fore.YELLOW + "Password must contain:")
            print(Fore.YELLOW + "At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char\n")
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
        
        user = cls.users[username]
        if not cls._check_password(password, user.__password_hash):
            print(Fore.RED + "Wrong password!\n")
            return None

        cls.current_user = user
        print(Fore.GREEN + f"Welcome back, {username}!\n")
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
                'name': pet.name,
                'type': pet.type,
                'age': pet.age,
                'happiness': pet.happiness,
                'hunger': pet.hunger,
                'sanity': pet.sanity,
                'health': pet.health,
                'fat': pet.fat,
                'energy': pet.energy,
                'generosity': pet.generosity
            }
            pets_data. append(pet_data)
        
        user_data = {
            'username': self.username,
            'password': self.__password_hash,  
            'currency': self._currency,
            'inventory': self.inventory,
            'music': self.music,
            'food': self.food,
            'pets': pets_data
        }
        
        return user_data
    
    def restore_from_memento(self, memento: Dict[str, Any]) -> None:
        from .animal import Cat, Rabbit, Dino, Dragon, Pou
        
        self.username = memento. get('username', self.username)
        self.__password_hash = memento.get('password', self.__password_hash)
        self._currency = memento. get('currency', 0)
        self.inventory = memento.get('inventory', self.inventory)
        self.music = memento.get('music', {})
        self.food = memento.get('food', {})
        
        self.pets = []
        pet_class_map = {
            'Cat': Cat,
            'Rabbit': Rabbit,
            'Dinosaur': Dino,
            'Dragon': Dragon,
            'Pou': Pou
        }
        
        for pet_data in memento.get('pets', []):
            pet_type = pet_data.get('type', 'Cat')
            pet_class = pet_class_map. get(pet_type, Cat)
            
            pet = pet_class(pet_data['name'], pet_data['age'])
            pet.happiness = pet_data.get('happiness', 50)
            pet.hunger = pet_data.get('hunger', 50)
            pet.sanity = pet_data.get('sanity', 50)
            pet.health = pet_data.get('health', 50)
            pet.fat = pet_data. get('fat', 0)
            pet.energy = pet_data.get('energy', 50)
            pet.generosity = pet_data.get('generosity', 0)
            
            self.pets.append(pet)
# user.py
from .pet import VirtualPet
import math
import string
from random import randrange

GARIS = "─────────────────────────────────────────────────────────────────────────────────────────────────────"
class User:
    users = {}      
    current_user = None  

    def __init__(self, username: str, password: str):
        self.username = username
        self.__password = password
        self.pets = []        
        self._currency = randrange(0,25000)
    
    @property
    def currency(self) -> int:
        return self._currency

    @currency.setter
    def currency(self, value) -> None:

        if (value < 0):
            print("\nCurrency cannot be below 0!")
        else:
            self._currency = value
    
    def limit_currency(self) -> None:
        for attr in ("currency"):
            val = int(getattr(self, attr))
            setattr(self, attr, max(0, min(math.inf, val)))
    
    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, new_password) -> None:

        total_digit = sum(ch.isdigit() for ch in new_password)
        total_symbol = sum(1 for ch in new_password if ch in string.punctuation)
        total_letter = sum(ch.isalpha() for ch in new_password)

        if (total_digit < 1 or total_letter < 8 or total_symbol < 2):
            print("\nChange password operation unsuccessful!")
            print("(Password must contain at least 1 digit, 8 letters, and 2 symbols)")
        else:
            self.__password = new_password

    def add_pet(self, pet: VirtualPet) -> None:
        self.pets.append(pet)

    @classmethod # agar bisa dipanggil tanpa harus membuat objek
    def register(cls, username: str, password: str) -> None:
        print()

        if username in cls.users:
            print("This username has already signed in!\n")
            return
        
        if username.strip().lower() in password.strip().lower():
            print("Password cannot be the same as username!\n")
            return
        
        for user in cls.users.values(): # mengecek apakah user mendaftar menggunakan password yang sama 
                                        # dengan user sebelumnya
            if (password == user.password):
                print("This password is already in used!\n")
                return

        total_digit = sum(ch.isdigit() for ch in password)
        total_symbol = sum(1 for ch in password if ch in string.punctuation)
        total_letter = sum(ch.isalpha() for ch in password)

        if total_digit < 1:
            print("Password must contain at least 1 digit!\n")
            print(GARIS)
            return

        if total_symbol < 2:
            print("Password must consist of at least 2 symbols!\n")
            print(GARIS)
            return

        if total_letter < 8:
            print("Password must consist of at least 8 letters!\n")
            print(GARIS)
            return

        new_user = cls(username, password)
        cls.users[username] = new_user

        cls.current_user = new_user
        print(f"User {username} registered successfully.\n")

    @classmethod
    def login(cls, username: str, password: str) -> None:
        print()
        if username not in cls.users:
            print("User not found!\n")
            return

        if cls.users[username].password != password:
            print("Wrong password!\n")
            return

        cls.current_user = cls.users[username]
        print(f"Welcome back, {username}!\n")

# user.py
from pet import VirtualPet
import string
from random import randrange

class User:
    users = {}          
    current_user = None  

    def __init__(self, username: str, password: str):
        self.username = username
        self.__password = password
        self.pets = []        
        self.currency = randrange(0,25000)
    
    def get_password(self) -> str:
        return self.__password

    def add_pet(self, pet: VirtualPet) -> None:
        self.pets.append(pet)

    @classmethod # agar bisa dipanggil tanpa harus membuat objek
    def register(cls, username: str, password: str) -> None:
        print()

        if username in cls.users:
            print("This username has already signed in!\n")
            return

        total_digit = sum(ch.isdigit() for ch in password)
        total_symbol = sum(1 for ch in password if ch in string.punctuation)
        total_letter = sum(ch.isalpha() for ch in password)

        if total_digit < 1:
            print("Password must contain at least one digit!\n")
            print("─────────────────────────────────────────────────────────────────────────────────────────────────────")
            return

        if total_symbol < 2:
            print("Password must consist of at least 2 symbols!\n")
            print("─────────────────────────────────────────────────────────────────────────────────────────────────────")
            return

        if total_letter < 8:
            print("Password must consist of at least 8 letters!\n")
            print("─────────────────────────────────────────────────────────────────────────────────────────────────────")
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

        if cls.users[username].get_password() != password:
            print("Wrong password!\n")
            return

        cls.current_user = cls.users[username]
        print(f"Welcome back, {username}!\n")

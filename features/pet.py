from random import randrange
from typing import Dict, Tuple
from .formatter import GARIS

FAT_BURNER = "Fat Burner"
HEALTH_POTION = "Health Potion"
ENERGIZER = "Energizer"
ADULT_POTION = "Adult Potion"

class VirtualPet:
    FOOD_DEF: Dict[str, Tuple[str, int, int]] = {
        "Kentucky Fried Chicken": ("🍗", 15, 5),
        "Ice Cream": ("🍦", 5, 3),
        "Fried Rice": ("🥘", 10, 0),
        "Salad": ("🥗", 10, -5),
        "French Fries": ("🍟", 5, 5),
        "Mashed Potato": ("🥔", 5, -2),
        "Mozarella Nugget": ("🧀", 20, 10),
    }

    SOAP_DEF: Dict[str, Tuple[str, int, int]] = {
        "Rainbow Bubble Soap": ("🌈", 50, 20),
        "Pink Bubble Soap": ("💗", 20, 10),
        "White Silk Soap": ("⚪", 10, 5),
        "Flower Bubble Soap": ("🌸", 30, 15),
    }

    POTION_DEF: Dict[str, Tuple[str, int]] = {
        FAT_BURNER: ("🧪", -50),
        HEALTH_POTION: ("💊", 50),
        ENERGIZER: ("⚡", 50),
        ADULT_POTION: ("💉", 20),
    }

    def __init__(self, name: str, age: float = 0, species: str = "Pet"):
        self.name: str = name
        self.age: float = age
        self.type: str = species
        self.happiness: int = randrange(0, 50)
        self.hunger: int = randrange(0, 50)
        self.sanity: int = randrange(0, 50)
        self.health: int = randrange(1, 50)
        self.fat: int = 0
        self.energy: int = randrange(0, 50)
        self.generosity = 0
        self.limit_stat()

    def get_mood(self) -> str:
        if self.happiness > 70 and self.energy > 50:
            return "Happy"
        elif self.happiness < 30 or self.energy < 20:
            return "Sad"
        elif self.happiness < 20:
            return "Stressed"
        else:
            return "Neutral"

    def get_summary(self) -> str:
        if self.health > 80:
            return "Healthy"
        elif self.health > 50:
            return "Okay"
        elif self.health > 20:
            return "Weak"
        elif self.health > 0:
            return "Critical"
        else:
            return "Dead"

    def get_age_summary(self) -> str:
        if self.age < 1:
            return "Baby"
        elif self.age < 3:
            return "Teen"
        elif self.age < 10:
            return "Adult"
        else:
            return "Elder"

    def limit_stat(self) -> None:
        for attr in ("sanity", "fat", "hunger", "happiness", "energy", "health"):
            val = int(getattr(self, attr))
            setattr(self, attr, max(0, min(100, val)))
        self.age = max(0.0, float(self.age))

    def time_past(self) -> None:
        self.hunger = max(0, self.hunger - 5)
        if self.hunger < 50:
            self.happiness = max(0, self.happiness - 5)
        if (self.hunger == 0) or (self.energy == 0):
            self.health = max(0, self.health - 5)
        self.age += 0.2
        self.limit_stat()

    def get_age(self) -> float:
        return self.age

    def feed(self, food: str) -> bool:
        emoji, hunger_change, happiness_change = VirtualPet.FOOD_DEF[food]

        if self.hunger >= 100:
            print(f"\n{self.name} doesn't want to eat anymore 🤢!")
            self.fat += 5
            return False

        print("\n" + "="*101)
        print(f"\n{self.name} has been fed with '{food}' {emoji} 🍽️.")

        self.hunger += int(hunger_change)
        self.happiness += int(happiness_change)
        self.limit_stat()

        print("="*101)
        print(f"{self.name}'s status: ")
        print("="*101)
        print(f"Fat: {self.fat}")
        print(f"Hunger: {self.hunger}")
        print(f"Happiness: {self.happiness}")
        print("="*101)
        return True

    def bath(self, soap: str) -> bool:
        emoji, sanity_change, happiness_change = VirtualPet.SOAP_DEF[soap]

        if self.sanity >= 100:
            print(f"\n{self.name}'s sanity is still full!\n")
            return False

        print("\n" + "="*101)
        self.sanity += int(sanity_change)
        self.happiness += int(happiness_change)

        print(f"\n{self.name} has been bathed 🛁 with '{soap}' {emoji}.")

        self.limit_stat()

        print("="*101)
        print(f"{self.name}'s status: ")
        print("="*101)
        print(f"Sanity: {self.sanity}")
        print(f"Happiness: {self.happiness}")
        print("="*101)
        return True

    def health_care(self, potion: str) -> bool:
        emoji, change = VirtualPet.POTION_DEF[potion]
        used = False

        if potion == FAT_BURNER and self.fat > 50:
            self.fat = max(0, self.fat - 50)
            print(f"\n{emoji} --> {self.name}'s fat has been reduced!\n")
            used = True
        elif potion == HEALTH_POTION and self.health < 100:
            self.health += int(change)
            print(f"\n{self.name} has been healed {emoji}!\n")
            used = True
        elif potion == ENERGIZER and self.energy < 100:
            self.energy += int(change)
            print(f"\n{emoji} --> {self.name}'s energy has been recharged 😆!\n")
            used = True
        elif potion == ADULT_POTION and self.age < 20:
            self.age += int(change)
            print(f"\n{emoji} --> {self.name} has leveled up to adult!\n")
            used = True
        else:
            print(f"\n{self.name} hasn't reached requirement to use {potion}!")

        if used:
            self.limit_stat()
            print("="*101)
            print(f"{self.name}'s status: ")
            print("="*101)
            print(f"Fat: {self.fat}")
            print(f"Health: {self.health}")
            print(f"Energy: {self.energy}")
            print("="*101)

        return used

    def sleep(self, hours: int) -> None:
        print("\n" + "="*101)
        if (hours < 4):
            print(f"{self.name} has a good nap 😴.")
            print(f"{self.name}'s energy increased by 10.")
            print(f"{self.name}'s hunger decreased by 4.")
            self.energy += 10
            self.hunger = max(0, self.hunger - 4)
        elif (4 <= hours <= 8):
            print(f"{self.name} has a good night sleep 😴.")
            print(f"{self.name}'s energy increased by 55.")
            print(f"{self.name}'s hunger decreased by 35.")
            self.energy += 55
            self.hunger = max(0, self.hunger - 35)
        elif (hours >= 12):
            print(f"{self.name} has too much sleep 😴.")
            print(f"{self.name}'s energy increased by 100.")
            print(f"{self.name}'s hunger decreased by 95.")
            self.energy += 100
            self.hunger = max(0, self.hunger - 95)

        self.limit_stat()

        print("\n" + GARIS)
        print(f"{self.name}'s status: ")
        print(GARIS)
        print(f"Energy: {self.energy}")
        print(f"Hunger: {self.hunger}")
        print(GARIS)
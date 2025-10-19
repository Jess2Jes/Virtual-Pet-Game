from random import randrange
from typing import Dict, Literal
from .formatter import Formatter
from .formatter import GARIS
from colorama import Fore, init
init(autoreset=True)

FAT_BURNER = "Fat Burner"
HEALTH_POTION = "Health Potion"
ENERGIZER = "Energizer"
ADULT_POTION = "Adult Potion"

PotionType = Literal["fat", "health", "energy", "age"]

class VirtualPet:
    FOOD_DEF: Dict[str, Dict[str, int | str]] = {
        "Kentucky Fried Chicken": {"emoji": "🍗", "hunger": 15, "happiness": 5, "price": 20000},
        "Ice Cream": {"emoji": "🍦", "hunger": 5, "happiness": 3, "price": 5000},
        "Fried Rice": {"emoji": "🥘", "hunger": 10, "happiness": 0, "price": 1000},
        "Salad": {"emoji": "🥗", "hunger": 10, "happiness": -5, "price": 5500},
        "French Fries": {"emoji": "🍟", "hunger": 5, "happiness": 5, "price": 30000},
        "Mashed Potato": {"emoji": "🥔", "hunger": 5, "happiness": -2, "price": 15000},
        "Mozarella Nugget": {"emoji": "🧀", "hunger": 20, "happiness": 10, "price": 25000},
    }

    SOAP_DEF: Dict[str, Dict[str, int | str]] = {
        "Rainbow Bubble Soap": {"emoji": "🌈", "sanity": 50, "happiness": 20, "price": 55000},
        "Pink Bubble Soap": {"emoji": "💗", "sanity": 20, "happiness": 10, "price": 35000},
        "White Silk Soap": {"emoji": "⚪", "sanity": 10, "happiness": 5, "price": 10000},
        "Flower Bubble Soap": {"emoji": "🌸", "sanity": 30, "happiness": 15, "price": 25000},
    }

    POTION_DEF: Dict[str, Dict[str, int | str | PotionType]] = {
        FAT_BURNER: {"emoji": "🧪", "type": "fat", "delta": -50, "price": 110000},
        HEALTH_POTION: {"emoji": "💊", "type": "health", "delta": 50, "price": 200000},
        ENERGIZER: {"emoji": "⚡", "type": "energy", "delta": 50, "price": 800000},
        ADULT_POTION: {"emoji": "💉", "type": "age", "delta": 20, "price": 1000000},
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
        self.format = Formatter()

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
        self.hunger -= 10
        if self.hunger < 50:
            self.happiness -= 5
        if (self.hunger == 0) or (self.energy == 0):
            self.health -= 10
        self.age += 0.2
        self.limit_stat()

    def get_age(self) -> float:
        return self.age
    
    def food_upgrade_stats(self) -> str:
        food_stats = {
            "fat": self.fat,
            "hunger": self.hunger,
            "happiness": self.happiness,
        }
        return self.format.format_upgrade_stats(self, food_stats)
    
    def bath_upgrade_stats(self) -> str:
        bath_stats = {
            "sanity": self.sanity,
            "happiness": self.happiness,
        }
        return self.format.format_upgrade_stats(self, bath_stats)
    
    def potion_upgrade_stats(self) -> str:
        potion_stats = {
            "fat": self.fat,
            "health": self.health,
            "energy": self.energy,
            "age": self.age,
        }
        return self.format.format_upgrade_stats(self, potion_stats)

    def sleep_upgrade_stats(self) -> str:
        sleep_stats = {
            "energy": self.fat,
            "hunger": self.hunger,
        }
        return self.format.format_upgrade_stats(self, sleep_stats)
    
    def joy_upgrade_stats(self) -> str:
        play_stats = {
            "happiness": self.happiness,
            "hunger": self.hunger,
            "energy": self.energy,
        }
        return self.format.format_upgrade_stats(self, play_stats)

    def play(self) -> None:
        self.happiness += 10
        self.hunger -= 5
        self.energy -= 5
        self.limit_stat()

    def feed(self, food: str) -> bool:
        data = VirtualPet.FOOD_DEF[food]
        emoji = data["emoji"]  
        hunger_change = int(data["hunger"]) 
        happiness_change = int(data["happiness"])  

        if self.hunger >= 100:
            print(Fore.RED + f"\n{self.name} doesn't want to eat anymore 🤢!\n")
            self.fat += 5
            self.limit_stat()
            return False

        print("\n" + "="*101)
        print(Fore.GREEN + f"\n{self.name} has been fed with '{food}' {emoji} 🍽️.")

        self.hunger += hunger_change
        self.happiness += happiness_change
        self.limit_stat()

        print(Fore.YELLOW + self.food_upgrade_stats())

        return True

    def bath(self, soap: str) -> bool:
        data = VirtualPet.SOAP_DEF[soap]
        emoji = data["emoji"]  
        sanity_change = int(data["sanity"])  
        happiness_change = int(data["happiness"])  

        if self.sanity >= 100:
            print(Fore.RED + f"\n{self.name}'s sanity is still full!\n")
            return False

        print("\n" + "="*101)
        self.sanity += sanity_change
        self.happiness += happiness_change

        print(Fore.GREEN + f"\n{self.name} has been bathed 🛁 with '{soap}' {emoji}.")

        self.limit_stat()

        print(Fore.YELLOW + self.bath_upgrade_stats())

        return True

    def health_care(self, potion: str) -> bool:
        data = VirtualPet.POTION_DEF[potion]
        emoji = data["emoji"]  
        effect_type: PotionType = data["type"]  
        delta = int(data["delta"])  

        used = False
        if effect_type == "fat" and self.fat > 50:
            self.fat = max(0, self.fat + delta)  
            print(f"\n{emoji} --> {self.name}'s fat has been reduced!\n")
            used = True
        elif effect_type == "health" and self.health < 100:
            self.health += delta
            print(f"\n{self.name} has been healed {emoji}!\n")
            used = True
        elif effect_type == "energy" and self.energy < 100:
            self.energy += delta
            print(f"\n{emoji} --> {self.name}'s energy has been recharged 😆!\n")
            used = True
        elif effect_type == "age" and self.age < 20:
            self.age += delta
            print(f"\n{emoji} --> {self.name} has leveled up to adult!\n")
            used = True

        if not used:
            print(Fore.RED + f"\n{self.name} hasn't reached requirement to use {potion}!\n")
            return False

        self.limit_stat()

        print(Fore.YELLOW + self.potion_upgrade_stats())

        return True

    def sleep(self, hours: int) -> None:

        if (self.energy >= 100):
            print(Fore.RED + f"\n{self.name} is not tired yet! 😐\n")
            return

        self.energy += hours * 10
        self.hunger -= hours * 5

        self.limit_stat()
        print(Fore.GREEN + f"\n{self.name} has slept for {hours} hours. 😴")
        print(f"{self.name}'s energy increased by {hours * 10}" \
               f" and hunger decreased by {hours * 5}.")
        
        print(Fore.YELLOW + self.sleep_upgrade_stats())
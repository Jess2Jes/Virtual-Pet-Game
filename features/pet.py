from random import randrange
from typing import Dict, List

FAT_BURNER = "Fat Burner"
HEALTH_POTION = "Health Potion"
ENERGIZER = "Energizer"
ADULT_POTION = "Adult Potion"

class VirtualPet:
    list_food: Dict[str, List[int]] = {
        "Kentucky Fried Chicken": [1, 15, 5],
        "Ice Cream": [1, 5, 3],
        "Fried Rice": [1, 10, 0],
        "Salad": [1, 10, -5],
        "French Fries": [1, 5, 5],
        "Mashed Potato": [2, 5, -2],
        "Mozarella Nugget": [1, 20, 10],
    }

    list_soap: Dict[str, List[int]] = {
        "Rainbow Bubble Soap": [1, 50, 20],  
        "Pink Bubble Soap": [2, 20, 10],
        "White Silk Soap": [1, 10, 5],
    }

    list_potion: Dict[str, List[int]] = {
        FAT_BURNER: [1, -50],     
        HEALTH_POTION: [2, 50],   
        ENERGIZER: [1, 50],       
        ADULT_POTION: [0, 20],    
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
        self.hunger = max(0, self.hunger - 1)
        if self.hunger < 50:
            self.happiness = max(0, self.happiness - 2)

        if (self.hunger == 0) or (self.energy == 0):
            self.health = max(0, self.health - 5)

        self.age += 0.2
        self.limit_stat()

    def get_age(self) -> float:
        return self.age

    def feed(self, food: str) -> None:
        print("="*101)
        if food not in VirtualPet.list_food:
            print(f"\nUnknown food: {food}\n")
            return

        if self.hunger >= 100:
            print(f"\n{self.name} doesn't want to eat anymore 🤢!\n")
            return

        _, hunger_change, happiness_change = VirtualPet.list_food[food]

        print(f"\n{self.name} has been fed with '{food}' 🍽️.\n")
        self.hunger += int(hunger_change)
        self.happiness += int(happiness_change)

        if self.hunger >= 100:
            self.fat += 5

        self.limit_stat()

        print("="*101)
        print(f"{self.name}'s status: ")
        print("="*101)
        print(f"Fat: {self.fat}")
        print(f"Hunger: {self.hunger}")
        print(f"Happiness: {self.happiness}")
        print("="*101)

    def bath(self, soap: str) -> None:
        print("="*101)
        if soap not in VirtualPet.list_soap:
            print(f"\nUnknown soap: {soap}\n")
            return

        if self.sanity >= 100:
            print(f"\n{self.name}'s sanity is still full!\n")
            return

        _, sanity_change, happiness_change = VirtualPet.list_soap[soap]
        self.sanity += int(sanity_change)
        self.happiness += int(happiness_change)
        print(f"\n{self.name} has been bathed 🛁 with '{soap}'.\n")

        self.limit_stat()

        print("="*101)
        print(f"{self.name}'s status: ")
        print("="*101)
        print(f"Sanity: {self.sanity}")
        print(f"Happiness: {self.happiness}")
        print("="*101)

    def health_care(self, potion: str) -> None:
        print("\n" + "="*101)
        if potion not in VirtualPet.list_potion:
            print(f"\nUnknown potion: {potion}\n")
            return

        _, value = VirtualPet.list_potion[potion]

        if potion == FAT_BURNER and self.fat > 50:
            self.fat = max(0, self.fat - 50)
            print(f"\n{self.name}'s fat has been reduced!\n")
        elif potion == FAT_BURNER:
            print(f"\n{self.name}'s fat hasn't reached 50!\n")

        elif potion == HEALTH_POTION and self.health < 100:
            self.health += int(value)
            print(f"\n{self.name} has been healed 💊!\n")

        elif potion == ENERGIZER and self.energy < 100:
            self.energy += int(value)
            print(f"\n{self.name}'s energy has been recharged 😆!\n")

        elif potion == ADULT_POTION and self.age < 20:
            self.age += int(value)
            print(f"\n{self.name} has leveled up to adult!\n")

        self.limit_stat()

        print("="*101)
        print(f"{self.name}'s status: ")
        print("="*101)
        print(f"Fat: {self.fat}")
        print(f"Health: {self.health}")
        print(f"Energy: {self.energy}")
        print("="*101)

    def sleep(self, hours: int) -> None:

        print("\n" + "="*101)
        if hours < 4:
            print(f"{self.name} has a good nap 😴.")
            print(f"{self.name}'s energy increased by 10.")
            print(f"{self.name}'s hunger decreased by 4.")
            self.energy += 10
            self.hunger = max(0, self.hunger - 4)

        elif 4 <= hours <= 8:
            print(f"{self.name} has a good night sleep 😴.")
            print(f"{self.name}'s energy increased by 55.")
            print(f"{self.name}'s hunger decreased by 35.")
            self.energy += 55
            self.hunger = max(0, self.hunger - 35)

        elif hours >= 12:
            print(f"{self.name} has too much sleep 😴.")
            print(f"{self.name}'s energy increased by 100.")
            print(f"{self.name}'s hunger decreased by 95.")
            self.energy += 100
            self.hunger = max(0, self.hunger - 95)

        self.limit_stat()

        print("\n" + "─"*101)
        print(f"{self.name}'s status: ")
        print("─"*101)
        print(f"Energy: {self.energy}")
        print(f"Hunger: {self.hunger}")
        print("─"*101)
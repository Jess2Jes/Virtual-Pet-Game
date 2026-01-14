# features/pet.py
from abc import ABC, abstractmethod
from random import randrange
from utils.formatter import Formatter
from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF
from utils.colorize import red, green, yellow
from utils.ports import ConsoleIO, OutputPort

"""
pet.py
Capabilities are split into granular interfaces.
Each capability interface defines specific actions that a pet can perform.
This modular design allows for flexible and maintainable pet entities
with distinct life capabilities.
"""


class Feedable(ABC):
    @abstractmethod
    def feed(self, food: str) -> bool: ...

class Playable(ABC):
    @abstractmethod
    def play(self) -> None: ...

class Batheable(ABC):
    @abstractmethod
    def bath(self, soap: str) -> bool: ...

class Treatable(ABC):
    @abstractmethod
    def health_care(self, potion: str) -> bool: ...

class Sleepable(ABC):
    @abstractmethod
    def sleep(self, hours: int) -> None: ...

class Observable(ABC):
    """Interface for viewing pet status."""
    @abstractmethod
    def get_mood_summary(self) -> str: ...
    @abstractmethod
    def get_health_summary(self) -> str: ...
    @abstractmethod
    def get_age_summary(self) -> str: ...


class AbstractPet(Feedable, Playable, Batheable, Treatable, Sleepable, Observable, ABC):
    """
    The cohesive Pet entity that implements all life capabilities.
    """
    def __init__(
        self,
        name: str,
        age: float = 0.0,
        species: str = "Pet",
        io: OutputPort | None = None
    ) -> None:
        self.name = name
        self.age = age
        self.type = species
        self.io = io or ConsoleIO()

    @abstractmethod
    def limit_stat(self) -> None:
        """Clamp stats to allowed ranges."""

    @abstractmethod
    def time_past(self) -> None:
        """Advance internal time."""


class VirtualPet(AbstractPet):
    """
    Default in-game pet implementation.
    """

    def __init__(
        self,
        name: str,
        age: float = 0.0,
        species: str = "Pet",
        io: OutputPort | None = None
    ) -> None:
        super().__init__(name, age, species, io)
        self.happiness: int = randrange(0, 50)
        self.hunger: int = randrange(0, 50)
        self.sanity: int = randrange(0, 50)
        self.health: int = randrange(1, 50)
        self.fat: int = 0
        self.energy: int = randrange(0, 50)
        self.generosity = 0
        self.format = Formatter()

    def get_mood_summary(self) -> str:
        """
        Get the current mood of the pet based on happiness and energy levels.
        """
        if self.happiness > 70 and self.energy > 50:
            return "Happy"
        elif self.happiness < 30 or self.energy < 20:
            return "Sad"
        elif self.happiness < 20:
            return "Stressed"
        else:
            return "Neutral"

    def get_health_summary(self) -> str:
        """
        Get a summary of the pet's health status.
        """
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
        """
        Get the age category of the pet.
        """
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
        """
        Get formatted upgrade stats after feeding.
        """
        return self.format.format_upgrade_stats(self, {"fat": self.fat, "hunger": self.hunger, "happiness": self.happiness})

    def bath_upgrade_stats(self) -> str:
        """
        Get formatted upgrade stats after bathing.
        """
        return self.format.format_upgrade_stats(self, {"sanity": self.sanity, "happiness": self.happiness})

    def potion_upgrade_stats(self) -> str:
        """ 
        Get formatted upgrade stats after health care.
        """
        return self.format.format_upgrade_stats(self, {"fat": self.fat, "health": self.health, "energy": self.energy, "age": self.age})

    def sleep_upgrade_stats(self) -> str:
        """ 
        Get formatted upgrade stats after sleeping.
        """
        return self.format.format_upgrade_stats(self, {"energy": self.energy, "hunger": self.hunger}) # Note: logic copied from original, check if 'fat' or 'energy' is intended for values

    def joy_upgrade_stats(self) -> str:
        """ 
        Get formatted upgrade stats after playing.
        """
        return self.format.format_upgrade_stats(self, {"happiness": self.happiness, "hunger": self.hunger, "energy": self.energy})

    def play(self) -> None:
        """ 
        Play with the pet to increase happiness.
        """
        self.happiness += 10
        self.hunger -= 5
        self.energy -= 5
        self.limit_stat()

    def feed(self, food: str) -> bool:
        """
        Feed the pet with specified food item.
        """
        data = FOOD_DEF[food]
        emoji = data["emoji"]
        hunger_change = int(data["hunger"])
        happiness_change = int(data["happiness"])

        if self.hunger >= 100:
            self.io.write(red(f"\n{self.name} doesn't want to eat anymore 🤢!\n"))
            self.fat += 5
            self.limit_stat()
            return False

        self.io.write("\n" + "="*120)
        self.io.write(green(f"\n{self.name} has been fed with '{food}' {emoji} 🍽️."))

        self.hunger += hunger_change
        self.happiness += happiness_change
        self.limit_stat()
        self.io.write(yellow(self.food_upgrade_stats()))
        return True

    def bath(self, soap: str) -> bool:
        """
        Bathe the pet with specified soap item.
        """
        data = SOAP_DEF[soap]
        emoji = data["emoji"]
        sanity_change = int(data["sanity"])
        happiness_change = int(data["happiness"])

        if self.sanity >= 100:
            self.io.write(red(f"\n{self.name}'s sanity is still full!\n"))
            return False

        self.io.write("\n" + "="*101)
        self.sanity += sanity_change
        self.happiness += happiness_change
        self.io.write(green(f"\n{self.name} has been bathed 🛁 with '{soap}' {emoji}."))
        self.limit_stat()
        self.io.write(yellow(self.bath_upgrade_stats()))
        return True

    def health_care(self, potion: str) -> bool:
        """
        Apply health care to the pet with specified potion item.
        """
        data = POTION_DEF[potion]
        emoji = data["emoji"]
        effect_type = data["type"]
        delta = int(data["delta"])

        used = False
        if effect_type == "fat" and self.fat > 50:
            self.fat = max(0, self.fat + delta)
            self.io.write(f"\n{emoji} --> {self.name}'s fat has been reduced!\n")
            used = True
        elif effect_type == "health" and self.health < 100:
            self.health += delta
            self.io.write(f"\n{self.name} has been healed {emoji}!\n")
            used = True
        elif effect_type == "energy" and self.energy < 100:
            self.energy += delta
            self.io.write(f"\n{emoji} --> {self.name}'s energy has been recharged 😆!\n")
            used = True
        elif effect_type == "age" and self.age < 20:
            self.age += delta
            self.io.write(f"\n{emoji} --> {self.name} has leveled up to adult!\n")
            used = True

        if not used:
            self.io.write(red(f"\n{self.name} hasn't reached requirement to use {potion}!\n"))
            return False

        self.limit_stat()
        self.io.write(yellow(self.potion_upgrade_stats()))
        return True

    def sleep(self, hours: int) -> None:
        """
        Allow the pet to sleep for a specified number of hours.
        """
        if self.energy >= 100:
            self.io.write(red(f"\n{self.name} is not tired yet! 😐\n"))
            return

        self.energy += hours * 10
        self.hunger -= hours * 5
        self.limit_stat()
        self.io.write(green(f"\n{self.name} has slept for {hours} hours. 😴"))
        self.io.write(f"{self.name}'s energy increased by {hours * 10} and hunger decreased by {hours * 5}.")
        self.io.write(yellow(self.sleep_upgrade_stats()))
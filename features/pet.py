"""
features/pet.py

Core domain models and capability interfaces for the Virtual Pet Game.

This module preserves the original behavior while providing:
- Segregated capability interfaces (ISP).
- A core `AbstractPet` identity model with an injected OutputPort (DIP).
- A `VirtualPet` concrete implementation of all standard capabilities.
"""

from abc import ABC, abstractmethod
from random import randrange

from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF
from utils.colorize import red, green, yellow
from utils.formatter import Formatter
from utils.ports import OutputPort

from features.pet_construction import NullOutputPort


class Feedable(ABC):
    """Interface for entities that can consume food."""

    @abstractmethod
    def feed(self, food: str) -> bool:
        """Feed the entity with the given food type and return whether it was accepted."""


class Playable(ABC):
    """Interface for entities that can be played with."""

    @abstractmethod
    def play(self) -> None:
        """Perform a play interaction that affects the entity's internal state."""


class Batheable(ABC):
    """Interface for entities that can be bathed."""

    @abstractmethod
    def bath(self, soap: str) -> bool:
        """Bathe the entity with the given soap type and return whether it was applied."""


class Treatable(ABC):
    """Interface for entities that can receive medical or potion treatment."""

    @abstractmethod
    def health_care(self, potion: str) -> bool:
        """Apply a potion treatment and return whether it took effect."""


class Sleepable(ABC):
    """Interface for entities that require sleep."""

    @abstractmethod
    def sleep(self, hours: int) -> None:
        """Put the entity to sleep for the specified hours."""


class Observable(ABC):
    """Interface for entities that report their status and mood."""

    @abstractmethod
    def get_mood(self) -> str:
        """Return a human-readable mood classification."""

    @abstractmethod
    def get_summary(self) -> str:
        """Return a health summary classification."""

    @abstractmethod
    def get_age_summary(self) -> str:
        """Return an age-based lifecycle classification."""


class AbstractPet(ABC):
    """
    Core identity model containing only identity attributes and I/O dependency.

    Collaboration:
    - Concrete pets inject an OutputPort (ConsoleIO, NullOutputPort, etc.).
    - Domain behaviors are implemented in subclasses (e.g., VirtualPet).
    """

    def __init__(self, name: str, io: OutputPort | None, age: float = 0.0, species: str = "Pet") -> None:
        self.name = name
        self.age = age
        self.type = species
        # Preserve original intent: pets require an IO mechanism.
        # To keep restoration behavior safe and consistent, a None IO is converted to a null port.
        self.io = io or NullOutputPort()


class VirtualPet(
    AbstractPet,
    Feedable,
    Playable,
    Batheable,
    Treatable,
    Sleepable,
    Observable,
):
    """
    Standard virtual pet that combines all life capabilities:
    eating, sleeping, playing, bathing, treatment, and status reporting.
    """

    def __init__(self, name: str, io: OutputPort | None, age: float = 0.0, species: str = "Pet") -> None:
        super().__init__(name, io, age, species)
        self.happiness: int = randrange(0, 50)
        self.hunger: int = randrange(0, 50)
        self.sanity: int = randrange(0, 50)
        self.health: int = randrange(1, 50)
        self.fat: int = 0
        self.energy: int = randrange(0, 50)
        self.generosity = 0
        self.format = Formatter()

    def get_mood(self) -> str:
        """Return mood derived from happiness and energy values."""
        if self.happiness > 70 and self.energy > 50:
            return "Happy"
        if self.happiness < 30 or self.energy < 20:
            return "Sad"
        if self.happiness < 20:
            return "Stressed"
        return "Neutral"

    def get_summary(self) -> str:
        """Return health classification derived from the pet's health stat."""
        if self.health > 80:
            return "Healthy"
        if self.health > 50:
            return "Okay"
        if self.health > 20:
            return "Weak"
        if self.health > 0:
            return "Critical"
        return "Dead"

    def get_age_summary(self) -> str:
        """Return lifecycle stage derived from the pet's age."""
        if self.age < 1:
            return "Baby"
        if self.age < 3:
            return "Teen"
        if self.age < 10:
            return "Adult"
        return "Elder"

    def limit_stat(self) -> None:
        """Clamp all stats to valid ranges and keep age non-negative."""
        for attr in ("sanity", "fat", "hunger", "happiness", "energy", "health"):
            val = int(getattr(self, attr))
            setattr(self, attr, max(0, min(100, val)))
        self.age = max(0.0, float(self.age))

    def time_past(self) -> None:
        """Simulate passage of time, decaying hunger/health and advancing age."""
        self.hunger -= 10
        if self.hunger < 50:
            self.happiness -= 5
        if (self.hunger <= 0) or (self.energy <= 0):
            self.health -= 10
        self.age += 0.2
        self.limit_stat()

    def get_age(self) -> float:
        """Return current age."""
        return self.age

    def food_upgrade_stats(self) -> str:
        """Return formatted stat changes after feeding."""
        return self.format.format_upgrade_stats(self, {"fat": self.fat, "hunger": self.hunger, "happiness": self.happiness})

    def bath_upgrade_stats(self) -> str:
        """Return formatted stat changes after bathing."""
        return self.format.format_upgrade_stats(self, {"sanity": self.sanity, "happiness": self.happiness})

    def potion_upgrade_stats(self) -> str:
        """Return formatted stat changes after potion use."""
        return self.format.format_upgrade_stats(
            self, {"fat": self.fat, "health": self.health, "energy": self.energy, "age": self.age}
        )

    def sleep_upgrade_stats(self) -> str:
        """Return formatted stat changes after sleeping."""
        return self.format.format_upgrade_stats(self, {"energy": self.energy, "hunger": self.hunger})

    def joy_upgrade_stats(self) -> str:
        """Return formatted stat changes after play."""
        return self.format.format_upgrade_stats(self, {"happiness": self.happiness, "hunger": self.hunger, "energy": self.energy})

    def play(self) -> None:
        """Increase happiness, reduce hunger and energy after play."""
        self.happiness += 10
        self.hunger -= 5
        self.energy -= 5
        self.limit_stat()

    def feed(self, food: str) -> bool:
        """Consume the provided food type and update hunger/fat/happiness."""
        data = FOOD_DEF[food]
        emoji = data["emoji"]
        hunger_change = int(data["hunger"])
        happiness_change = int(data["happiness"])

        if self.hunger >= 100:
            self.io.write(red(f"\n{self.name} doesn't want to eat anymore 🤢!\n"))
            self.fat += 5
            self.limit_stat()
            return False

        self.io.write("\n" + "=" * 120)
        self.io.write(green(f"\n{self.name} has been fed with '{food}' {emoji} 🍽️."))
        self.hunger += hunger_change
        self.happiness += happiness_change
        self.limit_stat()
        self.io.write(yellow(self.food_upgrade_stats()))
        return True

    def bath(self, soap: str) -> bool:
        """Apply a bath with the given soap, improving sanity and happiness."""
        data = SOAP_DEF[soap]
        emoji = data["emoji"]
        sanity_change = int(data["sanity"])
        happiness_change = int(data["happiness"])

        if self.sanity >= 100:
            self.io.write(red(f"\n{self.name}'s sanity is still full!\n"))
            return False

        self.io.write("\n" + "=" * 101)
        self.sanity += sanity_change
        self.happiness += happiness_change
        self.io.write(green(f"\n{self.name} has been bathed 🛁 with '{soap}' {emoji}."))
        self.limit_stat()
        self.io.write(yellow(self.bath_upgrade_stats()))
        return True

    def health_care(self, potion: str) -> bool:
        """Apply a potion effect when requirements are met."""
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
        """Recover energy and lose hunger based on hours slept."""
        if self.energy >= 100:
            self.io.write(red(f"\n{self.name} is not tired yet! 😐\n"))
            return

        self.energy += hours * 10
        self.hunger -= hours * 5
        self.limit_stat()
        self.io.write(green(f"\n{self.name} has slept for {hours} hours. 😴"))
        self.io.write(f"{self.name}'s energy increased by {hours * 10} and hunger decreased by {hours * 5}.")
        self.io.write(yellow(self.sleep_upgrade_stats()))
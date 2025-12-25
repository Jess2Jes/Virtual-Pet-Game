from abc import ABC, abstractmethod
from random import randrange
from .formatter import Formatter
from colorama import init
from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF
from utils.colorize import red, green, yellow
init(autoreset=True)

"""
pet.py

Defines the pet domain model for the Virtual Pet Game.

This module provides:
- An AbstractPet interface describing the public contract for all pet types.
- A concrete VirtualPet implementation with default stats, item definitions
  (food, soap, potion), and behaviors (feed, play, bath, health care, sleep, etc).

Notes:
- The VirtualPet class stores simple integer stats (0..100) and provides helper
  methods to render upgrade/status summaries using the Formatter utility.
- Potion/food/soap definitions are provided as class-level dictionaries to be
  referenced by shop/inventory code.
- This file focuses on behavior and in-memory state; persistence and user-facing
  interactions are managed elsewhere in the project.
"""


# Abstract Class
class AbstractPet(ABC):
    """
    Abstract base class that defines the minimal pet interface.

    Concrete pet classes must implement methods for mood/summary reporting and
    actions that change internal stats (play, feed, bath, health care, sleep).
    """

    def __init__(self, name: str, age: float = 0.0, species: str = "Pet") -> None:
        self.name: str = name
        self.age: float = age
        self.type: str = species

    @abstractmethod
    def get_mood(self) -> str:
        """Return a short string describing the pet's mood (e.g., 'Happy', 'Sad')."""

    @abstractmethod
    def get_summary(self) -> str:
        """Return a short health summary (e.g., 'Healthy', 'Critical')."""

    @abstractmethod
    def get_age_summary(self) -> str:
        """Return a life stage summary (e.g., 'Baby', 'Adult')."""

    @abstractmethod
    def limit_stat(self) -> None:
        """Clamp stats to allowed ranges (0..100 etc.)."""

    @abstractmethod
    def time_past(self) -> None:
        """Advance internal time and change stats appropriately."""

    @abstractmethod
    def play(self) -> None:
        """Play with the pet; modify stats accordingly."""

    @abstractmethod
    def feed(self, food: str) -> bool:
        """Feed the pet with the given food key; return True if consumed."""

    @abstractmethod
    def bath(self, soap: str) -> bool:
        """Bathe the pet with the given soap key; return True if applied."""

    @abstractmethod
    def health_care(self, potion: str) -> bool:
        """Apply a potion to the pet; return True if used."""

    @abstractmethod
    def sleep(self, hours: int) -> None:
        """Make the pet sleep for a number of hours; modify stats."""


class VirtualPet(AbstractPet):
    """
    Default in-game pet implementation used by the majority of gameplay flows.

    Attributes:
      - FOOD_DEF / SOAP_DEF / POTION_DEF: class-level definitions for items available
        in the shop and inventory. Each entry includes emoji, stat deltas and price.
      - name, age, type: identity fields.
      - happiness, hunger, sanity, health, fat, energy: core integer stats (roughly 0..100).
      - generosity: small counter used by conversation logic to limit gifts.
      - format: Formatter instance used to render status boxes for the CLI.
    """

    def __init__(self, name: str, age: float = 0.0, species: str = "Pet"):
        """
        Initialize a VirtualPet with randomized baseline stats.

        The randomized ranges are modest to simulate newly-created pets having variable starting values.
        """
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
        """
        Return a short textual mood description derived from happiness and energy.

        Note: the decision thresholds are intentionally simple and tuned for game feel.
        """
        if self.happiness > 70 and self.energy > 50:
            return "Happy"
        elif self.happiness < 30 or self.energy < 20:
            return "Sad"
        elif self.happiness < 20:
            return "Stressed"
        else:
            return "Neutral"

    def get_summary(self) -> str:
        """Return a short health summary string derived from the health stat."""
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
        """Return a textual life stage based on the age value."""
        if self.age < 1:
            return "Baby"
        elif self.age < 3:
            return "Teen"
        elif self.age < 10:
            return "Adult"
        else:
            return "Elder"

    def limit_stat(self) -> None:
        """
        Clamp core stats to sensible bounds.

        Ensures integer stats remain within 0..100 and age is non-negative.
        """
        for attr in ("sanity", "fat", "hunger", "happiness", "energy", "health"):
            val = int(getattr(self, attr))
            setattr(self, attr, max(0, min(100, val)))
        self.age = max(0.0, float(self.age))

    def time_past(self) -> None:
        """
        Simulate the passage of (game) time: decrease hunger and potentially happiness/health,
        then age the pet slightly and clamp stats.
        """
        self.hunger -= 10
        if self.hunger < 50:
            self.happiness -= 5
        if (self.hunger == 0) or (self.energy == 0):
            self.health -= 10
        self.age += 0.2
        self.limit_stat()

    def get_age(self) -> float:
        """Return the pet's age (float, game-specific units)."""
        return self.age

    # The following helper methods produce formatted upgrade/status boxes
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
        """Increase happiness and reduce hunger/energy as a result of playing."""
        self.happiness += 10
        self.hunger -= 5
        self.energy -= 5
        self.limit_stat()

    def feed(self, food: str) -> bool:
        """
        Consume a food item and apply its stat changes.

        Returns:
            True if the pet consumed the food; False if it refused (e.g., already full).
        """
        data = FOOD_DEF[food]
        emoji = data["emoji"]
        hunger_change = int(data["hunger"])
        happiness_change = int(data["happiness"])

        if self.hunger >= 100:
            print(red(f"\n{self.name} doesn't want to eat anymore 🤢!\n"))
            self.fat += 5
            self.limit_stat()
            return False

        print("\n" + "="*101)
        print(green(f"\n{self.name} has been fed with '{food}' {emoji} 🍽️."))

        self.hunger += hunger_change
        self.happiness += happiness_change
        self.limit_stat()

        print(yellow(self.food_upgrade_stats()))

        return True

    def bath(self, soap: str) -> bool:
        """
        Apply a soap/bath action and modify sanity/happiness.

        Returns:
            True if bathing was applied; False if pet already had full sanity.
        """
        data = SOAP_DEF[soap]
        emoji = data["emoji"]
        sanity_change = int(data["sanity"])
        happiness_change = int(data["happiness"])

        if self.sanity >= 100:
            print(red(f"\n{self.name}'s sanity is still full!\n"))
            return False

        print("\n" + "="*101)
        self.sanity += sanity_change
        self.happiness += happiness_change

        print(green(f"\n{self.name} has been bathed 🛁 with '{soap}' {emoji}."))

        self.limit_stat()

        print(yellow(self.bath_upgrade_stats()))
        return True

    def health_care(self, potion: str) -> bool:
        """
        Apply a potion to the pet if requirements are met.


        Returns:
            True if potion was applied and caused a change, False otherwise.
        """
        data = POTION_DEF[potion]
        emoji = data["emoji"]
        effect_type = data["type"]
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
            print(red(f"\n{self.name} hasn't reached requirement to use {potion}!\n"))
            return False

        self.limit_stat()

        print(yellow(self.potion_upgrade_stats()))

        return True

    def sleep(self, hours: int) -> None:
        """
        Put the pet to sleep for the specified number of hours.

        This increases energy and reduces hunger proportionally to hours slept,
        then clamps stats and prints an upgrade summary.
        """
        if self.energy >= 100:
            print(red(f"\n{self.name} is not tired yet! 😐\n"))
            return

        self.energy += hours * 10
        self.hunger -= hours * 5

        self.limit_stat()
        print(green(f"\n{self.name} has slept for {hours} hours. 😴"))
        print(f"{self.name}'s energy increased by {hours * 10}" \
               f" and hunger decreased by {hours * 5}.")

        print(yellow(self.sleep_upgrade_stats()))
"""
features/actions.py

Game action implementations using the Command Pattern.

Responsibilities:
- Encapsulate the logic, validation, and feedback for specific pet interactions.
- Decouple the 'Game' controller from the specific implementation details of actions.
- Utilize centralized configuration classes for game balance and text constants.
"""

from typing import Protocol, Any
from abc import abstractmethod
from random import randrange

from utils.ports import IOPort
from utils.colorize import red, green, yellow
from features.games.inventory_catalog import InventoryCatalog
from features.pet import VirtualPet
from constants.configs import (
    UIConfig, PlayConfig, WalkConfig,
    FoodConfig, SoapConfig, PotionConfig
)


class PetAction(Protocol):
    """Interface for any executable action a user can perform on a pet."""
    
    @abstractmethod
    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        """
        Execute the action logic.

        Args:
            pet: The target virtual pet instance.
            user: The current user (for currency/inventory updates).
            io: The input/output port for displaying messages.
        """
        ...


class PlayAction(PetAction):
    """
    Command that handles the logic, validation, and output for playing with a pet.
    """

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        if pet.energy < PlayConfig.ENERGY_COST:
            io.write(red(f"\n{pet.name} is too tired to play..\n"))
            return
        if pet.hunger < PlayConfig.HUNGER_COST:
            io.write(red(f"\n{pet.name} is too hungry to play..\n"))
            return
        if pet.health < PlayConfig.HEALTH_REQ:
            io.write(red(f"\n{pet.name} is too sick to play..\n"))
            return

        act = PlayConfig.FLAVOR_TEXT.get(pet.type.lower(), PlayConfig.FLAVOR_TEXT["default"])
        emoji = PlayConfig.EMOJIS.get(pet.type.lower(), PlayConfig.EMOJIS["default"])
        
        io.write(green(f"\n{act} {pet.name} {emoji}!"))

        pet.play() 

        io.write(f"\n{pet.name}'s happiness increased by {PlayConfig.HAPPINESS_GAIN}.")
        io.write(f"{pet.name}'s hunger decreased by {PlayConfig.HUNGER_DECREASE}.")
        io.write(f"{pet.name}'s energy decreased by {PlayConfig.ENERGY_DECREASE}.")
        
        io.write(f"You earned Rp. {PlayConfig.MONEY_REWARD:,}!")
        user.currency += PlayConfig.MONEY_REWARD

        io.write(yellow(pet.joy_upgrade_stats()))


class WalkAction(PetAction):
    """
    Command that handles the logic for taking a pet for a walk.
    Includes handling of random events (finding money, accidents, robbery).
    """

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        if pet.energy < WalkConfig.ENERGY_REQ:
            io.write(red(f"\n{pet.name} is too tired to take a walk..\n"))
            return
        if pet.hunger < WalkConfig.HUNGER_REQ:
            io.write(red(f"\n{pet.name} is too hungry to take a walk..\n"))
            return
        if pet.health < WalkConfig.HEALTH_REQ:
            io.write(red(f"\n{pet.name} is too sick to take a walk..\n"))
            return

        random_event = randrange(0, 50)
        
        io.write(green(f"\nYou take {pet.name} for a walk! 🐾"))

        if random_event == 10:
            io.write(green("\nYou found a wallet in your way home!"))
            io.write(green(f"You brought back home Rp. {WalkConfig.FOUND_MONEY:,}..."))
            user.currency += WalkConfig.FOUND_MONEY
            
        elif random_event == 30:
            io.write(red("\nYour pet stepped on mud!"))
            io.write(yellow(f"{pet.name}'s sanity decreased (-{WalkConfig.MUD_SANITY_LOSS})..."))
            pet.sanity -= WalkConfig.MUD_SANITY_LOSS
            
        elif random_event == 20:
            io.write(red("\nYour pet ate rotten apple!"))
            io.write(yellow(f"{pet.name}'s health decreased (-{WalkConfig.ROTTEN_HEALTH_LOSS})..."))
            pet.health -= WalkConfig.ROTTEN_HEALTH_LOSS
            
        elif random_event == 4:
            io.write(red("\nYour pet got run over by car!"))
            io.write(red(f"{pet.name} deceased... 💀\n"))
            pet.health -= 100
            pet.limit_stat()
            return 
            
        elif random_event == 50:
            io.write(red("\nYou got robbed on your way home!"))
            io.write(red(f"You lose Rp. {WalkConfig.LOST_MONEY:,}!"))
            user.currency -= WalkConfig.LOST_MONEY
            user.limit_currency()

        pet.happiness += WalkConfig.HAPPINESS_GAIN
        pet.hunger -= WalkConfig.HUNGER_COST
        pet.energy -= WalkConfig.ENERGY_COST

        io.write(f"{pet.name}'s hunger decreased by {WalkConfig.HUNGER_COST}.")
        io.write(f"{pet.name}'s energy decreased by {WalkConfig.ENERGY_COST}.")

        pet.limit_stat()
        io.write(yellow(pet.joy_upgrade_stats()))


class FeedAction(PetAction):
    """
    Command that handles feeding the pet.
    Resolves user numeric input to food names using FoodConfig.
    """
    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        food_num = io.read("\nWhich food (1/2/3/4/5/6/7)? ").strip()
        
        choice = FoodConfig.CHOICE_MAP.get(food_num)
        if not choice:
            io.write(red("\nUnknown food choice! Please choose (1/2/3/4/5/6/7)!\n"))
            return

        inv = user.inventory["food"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {UIConfig.NO_STOCK_MSG}. Buy more in the shop before feeding.\n"))
            return

        used = pet.feed(choice)
        if used:
            user.consume_item("food", choice, 1)
            
            remaining = user.inventory["food"][choice]
            emoji = str(self._catalog.food_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")


class BathAction(PetAction):
    """
    Command that handles bathing the pet.
    Resolves user numeric input to soap names using SoapConfig.
    """
    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        soap_num = io.read("\nWhich soap (1/2/3/4)? ").strip()
        
        choice = SoapConfig.CHOICE_MAP.get(soap_num)
        if not choice:
            io.write(red("\nUnknown soap choice! Please choose (1/2/3/4)!\n"))
            return

        inv = user.inventory["soap"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {UIConfig.NO_STOCK_MSG}. Buy more in the shop before bathing.\n"))
            return

        used = pet.bath(choice)
        if used:
            user.consume_item("soap", choice, 1)
            
            remaining = user.inventory["soap"][choice]
            emoji = str(self._catalog.soap_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")


class PotionAction(PetAction):
    """
    Command that handles giving a potion to a pet.
    Resolves user numeric input to potion names using PotionConfig.
    """
    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        self._print_requirements(io)

        potion_num = io.read("\nWhich potion (1/2/3/4)? ").strip()
        
        choice = PotionConfig.CHOICE_MAP.get(potion_num)
        if not choice:
            io.write(red("\nUnknown potion choice! Please choose (1/2/3/4)!\n"))
            return

        inv = user.inventory["potion"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {UIConfig.NO_STOCK_MSG}. Buy more in the shop before using.\n"))
            return

        used = pet.health_care(choice)
        if used:
            user.consume_item("potion", choice, 1)
            remaining = user.inventory["potion"][choice]
            emoji = str(self._catalog.potion_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")

    def _print_requirements(self, io: IOPort) -> None:
        """Displays the specific rules for using potions."""
        lines = [
            "",
            UIConfig.LINE,
            "Potion Usage Requirement",
            UIConfig.LINE,
            "1. Fat Burner can be used if your energy is below 50.",
            "2. Health Potion can be used if your health is below 100.",
            "3. Energizer can be used if your energy is below 100.",
            "4. Adult Potion can be used if your age is below 20.",
            UIConfig.LINE + "\n",
        ]
        io.write("\n".join(lines))
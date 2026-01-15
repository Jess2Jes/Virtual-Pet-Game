"""
features/actions.py

Game action implementations using the Command Pattern.

Responsibilities:
- Encapsulate the logic, validation, and feedback for specific pet interactions.
- Decouple the 'Game' controller from the specific implementation details of actions.
"""

from typing import Protocol, Any
from abc import abstractmethod
from random import randrange

from utils.ports import IOPort
from utils.colorize import red, green, yellow
from features.games.inventory_catalog import InventoryCatalog
from features.pet import VirtualPet
from constants.configs import NO_STOCK_MSG, LINE


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
        energy_cost = 10
        hunger_cost = 30
        health_req = 20
        
        happiness_gain = 10
        hunger_decrease = 5
        energy_decrease = 5
        money_reward = 25000

        if pet.energy < energy_cost:
            io.write(red(f"\n{pet.name} is too tired to play..\n"))
            return
        if pet.hunger < hunger_cost:
            io.write(red(f"\n{pet.name} is too hungry to play..\n"))
            return
        if pet.health < health_req:
            io.write(red(f"\n{pet.name} is too sick to play..\n"))
            return

        act_map = {
            "cat": "You play laser with",
            "rabbit": "You play catch ball with",
            "dinosaur": "You play hide and seek with",
            "dragon": "You play fireball with",
            "pou": "You brought to swimming pool",
        }
        emoji_map = {
            "cat": "💥",
            "rabbit": "🤾",
            "dinosaur": "🏃",
            "dragon": "☄️",
            "pou": "🏊‍♂️"
        }
        
        act = act_map.get(pet.type.lower(), "You play with")
        emoji = emoji_map.get(pet.type.lower(), "🎲")
        
        io.write(green(f"\n{act} {pet.name} {emoji}!"))

        pet.play() 

        io.write(f"\n{pet.name}'s happiness increased by {happiness_gain}.")
        io.write(f"{pet.name}'s hunger decreased by {hunger_decrease}.")
        io.write(f"{pet.name}'s energy decreased by {energy_decrease}.")
        
        io.write(f"You earned Rp. {money_reward:,}!")
        user.currency += money_reward

        io.write(yellow(pet.joy_upgrade_stats()))


class WalkAction(PetAction):
    """
    Command that handles the logic for taking a pet for a walk.
    Includes handling of random events (finding money, accidents, robbery).
    """

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        energy_req = 10
        hunger_req = 30
        health_req = 20
        
        happiness_gain = 25
        hunger_cost = 5
        energy_cost = 15
        lost_money = 100000
        found_money = 25000

        if pet.energy < energy_req:
            io.write(red(f"\n{pet.name} is too tired to take a walk..\n"))
            return
        if pet.hunger < hunger_req:
            io.write(red(f"\n{pet.name} is too hungry to take a walk..\n"))
            return
        if pet.health < health_req:
            io.write(red(f"\n{pet.name} is too sick to take a walk..\n"))
            return

        random_event = randrange(0, 50)
        
        io.write(green(f"\nYou take {pet.name} for a walk! 🐾"))

        if random_event == 10:
            io.write(green("\nYou found a wallet in your way home!"))
            io.write(green(f"You brought back home Rp. {found_money:,}..."))
            user.currency += found_money
            
        elif random_event == 30:
            io.write(red("\nYour pet stepped on mud!"))
            io.write(yellow(f"{pet.name}'s sanity decreased (-10)..."))
            pet.sanity -= 10
            
        elif random_event == 20:
            io.write(red("\nYour pet ate rotten apple!"))
            io.write(yellow(f"{pet.name}'s health decreased (-15)..."))
            pet.health -= 15
            
        elif random_event == 4:
            io.write(red("\nYour pet got run over by car!"))
            io.write(red(f"{pet.name} deceased... 💀\n"))
            pet.health -= 100
            pet.limit_stat()
            return 
            
        elif random_event == 50:
            io.write(red("\nYou got robbed on your way home!"))
            io.write(red(f"You lose Rp. {lost_money:,}!"))
            user.currency -= lost_money
            user.limit_currency()

        pet.happiness += happiness_gain
        pet.hunger -= hunger_cost
        pet.energy -= energy_cost

        io.write(f"{pet.name}'s hunger decreased by {hunger_cost}.")
        io.write(f"{pet.name}'s energy decreased by {energy_cost}.")

        pet.limit_stat()
        io.write(yellow(pet.joy_upgrade_stats()))


class FeedAction(PetAction):
    """
    Command that handles feeding the pet.
    Resolves user numeric input to food names and validates inventory stock.
    """
    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        food_num = io.read("\nWhich food (1/2/3/4/5/6/7)? ").strip()
        
        choice = self._resolve_choice(food_num, io)
        if not choice:
            return

        inv = user.inventory["food"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {NO_STOCK_MSG}. Buy more in the shop before feeding.\n"))
            return

        used = pet.feed(choice)
        if used:
            user.consume_item("food", choice, 1)
            
            remaining = user.inventory["food"][choice]
            emoji = str(self._catalog.food_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")

    def _resolve_choice(self, num: str, io: IOPort) -> str | None:
        food_choice_map = {
            "1": "kentucky fried chicken", "2": "ice cream", "3": "fried rice",
            "4": "salad", "5": "french fries", "6": "mashed potato",
            "7": "mozarella nugget",
        }
        try:
            return food_choice_map[num].title()
        except KeyError:
            io.write(red("\nUnknown food choice! Please choose (1/2/3/4/5/6/7)!\n"))
            return None


class BathAction(PetAction):
    """
    Command that handles bathing the pet.
    Resolves user numeric input to soap names and validates inventory stock.
    """
    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        soap_num = io.read("\nWhich soap (1/2/3/4)? ").strip()
        
        choice = self._resolve_choice(soap_num, io)
        if not choice:
            return

        inv = user.inventory["soap"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {NO_STOCK_MSG}. Buy more in the shop before bathing.\n"))
            return

        used = pet.bath(choice)
        if used:
            user.consume_item("soap", choice, 1)
            
            remaining = user.inventory["soap"][choice]
            emoji = str(self._catalog.soap_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")

    def _resolve_choice(self, num: str, io: IOPort) -> str | None:
        soap_choice_map = {
            "1": "rainbow bubble soap", "2": "pink bubble soap",
            "3": "white silk soap", "4": "flower bubble soap",
        }
        try:
            return soap_choice_map[num].title()
        except KeyError:
            io.write(red("\nUnknown soap choice! Please choose (1/2/3/4)!\n"))
            return None


class PotionAction(PetAction):
    """
    Command that handles giving a potion to a pet.
    Displays usage requirements, validates input/stock, and applies health care effects.
    """
    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        self._print_requirements(io)

        potion_num = io.read("\nWhich potion (1/2/3/4)? ").strip()
        choice = self._resolve_choice(potion_num, io)
        if not choice:
            return

        inv = user.inventory["potion"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {NO_STOCK_MSG}. Buy more in the shop before using.\n"))
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
            LINE,
            "Potion Usage Requirement",
            LINE,
            "1. Fat Burner can be used if your energy is below 50.",
            "2. Health Potion can be used if your health is below 100.",
            "3. Energizer can be used if your energy is below 100.",
            "4. Adult Potion can be used if your age is below 20.",
            LINE + "\n",
        ]
        io.write("\n".join(lines))

    def _resolve_choice(self, num: str, io: IOPort) -> str | None:
        potion_choice_map = {
            "1": "fat burner",
            "2": "health potion",
            "3": "energizer",
            "4": "adult potion",
        }
        try:
            return potion_choice_map[num].title()
        except KeyError:
            io.write(red("\nUnknown potion choice! Please choose (1/2/3/4)!\n"))
            return None
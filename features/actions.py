"""
features/actions.py

Implements the Command Pattern for pet interactions. Each action encapsulates 
the logic, UI rendering, and state mutations required for a specific gameplay feature.
"""

from typing import Protocol, Any
from abc import abstractmethod
from random import randrange, choice as ch

from utils.ports import IOPort
from utils.colorize import red, green, yellow, cyan
from features.games.inventory_catalog import InventoryCatalog
from features.pet import VirtualPet
from features.games.topic_handlers import ConversationEngine
from features.games.game_io_views import GameView
from constants.configs import (
    UIConfig, PlayConfig, WalkConfig,
    FoodConfig, SoapConfig, PotionConfig
)


class PetAction(Protocol):
    """Protocol defining the contract for executable game commands."""
    
    @property
    @abstractmethod
    def menu_name(self) -> str:
        """Display name for the action in the interaction menu."""
        ...

    @abstractmethod
    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        """Executes the action's business logic and UI flow."""
        ...


class StockPrinter:
    """Mixin for rendering inventory stock lists efficiently."""
    
    @staticmethod
    def print_stock(io: IOPort, title: str, defs: dict, inventory: dict, category: str) -> None:
        lines = ["", UIConfig.LINE, title, UIConfig.LINE + "\n"]
        is_food = category == "food"
        is_soap = category == "soap"

        for idx, (key, v) in enumerate(defs.items(), start=1):
            emoji = str(v["emoji"])
            qty = inventory.get(key, 0)
            stock_text = f"{qty}" if qty > 0 else f"{red(UIConfig.NO_STOCK_MSG)}"
            
            if is_food:
                lines.append(f"{idx}. {key} {emoji} (Hunger: {v['hunger']}, Happiness: {v['happiness']}, Available: {stock_text})")
            elif is_soap:
                lines.append(f"{idx}. {key} {emoji} (Sanity: {v['sanity']}, Happiness: {v['happiness']}, Available: {stock_text})")
            else:
                lines.append(f"{idx}. {key} {emoji} (Available: {stock_text}, Effect: {v['delta']})")
        
        io.write("\n".join(lines))


class PlayAction(PetAction):
    menu_name = "Play"

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
    menu_name = "Take a walk"

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


class FeedAction(PetAction, StockPrinter):
    menu_name = "Feed"

    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        self.print_stock(io, "List of Foods:", self._catalog.food_defs(), user.inventory["food"], "food")

        food_num = io.read("\nWhich food (1/2/3/4/5/6/7)? ").strip()
        choice = FoodConfig.CHOICE_MAP.get(food_num)
        
        if not choice:
            io.write(red("\nUnknown food choice! Please choose (1/2/3/4/5/6/7)!\n"))
            return

        inv = user.inventory["food"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {UIConfig.NO_STOCK_MSG}. Buy more in the shop before feeding.\n"))
            return

        if pet.feed(choice):
            user.consume_item("food", choice, 1)
            remaining = user.inventory["food"][choice]
            emoji = str(self._catalog.food_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")


class BathAction(PetAction, StockPrinter):
    menu_name = "Bath"

    def __init__(self, catalog: InventoryCatalog):
        self._catalog = catalog

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        self.print_stock(io, "List of Soaps:", self._catalog.soap_defs(), user.inventory["soap"], "soap")

        soap_num = io.read("\nWhich soap (1/2/3/4)? ").strip()
        choice = SoapConfig.CHOICE_MAP.get(soap_num)
        
        if not choice:
            io.write(red("\nUnknown soap choice! Please choose (1/2/3/4)!\n"))
            return

        inv = user.inventory["soap"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {UIConfig.NO_STOCK_MSG}. Buy more in the shop before bathing.\n"))
            return

        if pet.bath(choice):
            user.consume_item("soap", choice, 1)
            remaining = user.inventory["soap"][choice]
            emoji = str(self._catalog.soap_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")


class PotionAction(PetAction, StockPrinter):
    menu_name = "Give Potion"

    def __init__(self, catalog: InventoryCatalog, view: GameView):
        self._catalog = catalog
        self._view = view

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        self.print_stock(io, "List of Potions:", self._catalog.potion_defs(), user.inventory["potion"], "potion")
        self._view.print_potion_requirement("Potion Usage Requirement")

        potion_num = io.read("\nWhich potion (1/2/3/4)? ").strip()
        choice = PotionConfig.CHOICE_MAP.get(potion_num)
        
        if not choice:
            io.write(red("\nUnknown potion choice! Please choose (1/2/3/4)!\n"))
            return

        inv = user.inventory["potion"]
        if inv.get(choice, 0) <= 0:
            io.write(red(f"\n{choice} is {UIConfig.NO_STOCK_MSG}. Buy more in the shop before using.\n"))
            return

        if pet.health_care(choice):
            user.consume_item("potion", choice, 1)
            remaining = user.inventory["potion"][choice]
            emoji = str(self._catalog.potion_defs()[choice]["emoji"])
            io.write(f"Remaining {choice} ({emoji}): {remaining}\n")


class SleepAction(PetAction):
    menu_name = "Sleep"

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        try:
            hours = int(io.read(f"\n{pet.name}'s sleep duration (1-12): "))
        except ValueError:
            io.write(red("\nPlease insert digit at choice input!\n"))
            return

        if not (1 <= hours <= 12):
            io.write(red("\nSleep duration must between 1 to 12 hours.\n"))
            return

        pet.sleep(hours)


class TalkAction(PetAction):
    menu_name = "Talk to pet"

    def __init__(self, engine: ConversationEngine, view: GameView, jokes: list, conversations: list):
        self._engine = engine
        self._view = view
        self._jokes = jokes
        self._conversations = conversations

    def execute(self, pet: VirtualPet, user: Any, io: IOPort) -> None:
        while True:
            self._view.print_talk_menu()
            try:
                topic = int(io.read("Choose a topic: "))
            except ValueError:
                io.write(red("\nPlease type a number."))
                continue

            if topic == 1: 
                self._topic_plan(pet, io)
            elif topic == 2: 
                io.write(cyan(f"\n{pet.name} {pet.emoji} : My favourite food is {pet.fav_food}. :D"))
            elif topic == 3: 
                self._topic_conversation_menu(pet, io)
            elif topic == 4: 
                self._topic_money(pet, user, io)
            elif topic == 5: 
                self._topic_joke(pet, io)
            elif topic == 6: 
                io.write(cyan(f"\n{pet.name} {pet.emoji} : Okay, goodbye!"))
                io.write(green(f"{pet.name}'s happiness has increased by 10.\n"))
                pet.happiness += 10
                break
            else:
                io.write(red("\nPlease choose based on choices we have!"))

    def _topic_plan(self, pet: VirtualPet, io: IOPort):
        ans = [
            f"I want to eat {pet.fav_food}!",
            "I want to play :D",
            "I want to take a walk 🌳.",
            "I want to take a bath :)",
            "I want to talk to you..👉👈",
        ]
        io.write(cyan(f"\n{pet.name} {pet.emoji} : {ch(ans)}"))

    def _topic_conversation_menu(self, pet: VirtualPet, io: IOPort):
        while True:
            self._view.print_conversation_menu()
            io.write(cyan(f"\n{pet.name} {pet.emoji} : What would you like to talk today? "))
            
            try:
                topic = int(io.read("Choose a topic: "))
            except ValueError:
                io.write(red("\nPlease type a number."))
                continue

            actions = {
                1: lambda: self._handle_music_topic(pet, io),
                2: lambda: self._handle_food_topic(pet, io),
                3: lambda: self._end_topic(pet, io)
            }

            handler = actions.get(topic)
            if handler is None:
                io.write(red("\nPlease choose based on choices we have!"))
                continue
            
            keep_talking = handler()
            if keep_talking is False:
                break

    def _handle_music_topic(self, pet: VirtualPet, io: IOPort) -> bool:
        if not self._conversations:
             io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!"))
             return False

        return self._engine.handle_random_topic_of_type(pet, self._conversations, "Music Taste")

    def _handle_food_topic(self, pet: VirtualPet, io: IOPort) -> bool:
        if not self._conversations:
             io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!"))
             return False

        return self._engine.handle_random_topic_of_type(pet, self._conversations, "Favourite Food/Drink")

    def _end_topic(self, pet: VirtualPet, io: IOPort) -> bool:
        io.write(cyan(f"\n{pet.name} {pet.emoji} : Okay, I have gotten to know you more, thanks for sharing yours!"))
        io.write(green(f"{pet.name}'s happiness has increased by 10."))
        pet.happiness += 10
        return False 

    def _topic_money(self, pet: VirtualPet, user: Any, io: IOPort):
        if all(val < 50 for val in [pet.hunger, pet.sanity, pet.happiness, pet.health]):
            io.write(cyan(f"\n{pet.name} {pet.emoji} : I will consider it if you take care of me properly!\n"))
            return

        if pet.generosity < 2:
            io.write(cyan(f"\n{pet.name} {pet.emoji} : Here, I'll give you Rp. 100,000."))
            user.currency += 100000
            pet.generosity += 1
        else:
            io.write(cyan(f"\n{pet.name} {pet.emoji} : Sorry, can't give you anymore... 😔\n"))

    def _topic_joke(self, pet: VirtualPet, io: IOPort):
        if pet.hunger < 30:
            io.write(red(f"\n{pet.name} is too hungry to joke right now..\n"))
            return
        if pet.health < 20:
            io.write(red(f"\n{pet.name} is too sick to joke right now..\n"))
            return
        if pet.energy < 10:
            io.write(red(f"\n{pet.name} is too tired to joke right now..\n"))
            return
        if pet.happiness < 20:
            io.write(red(f"\n{pet.name} is too stressed to joke right now..\n"))
            return

        if not self._jokes:
             io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of jokes right now! Sorry!"))
             return
        
        random_joke = ch(self._jokes)
        
        question = random_joke.get("question", "")
        answer_expected = random_joke.get("answer", "")
        
        ans = io.read(cyan(f"\n{pet.name} {pet.emoji} : {question} ")).strip()

        if ans.lower() == (answer_expected or "").lower():
            io.write(cyan(f"\n{pet.name} {pet.emoji} : Wait! How did you know? 😱"))
            io.write(cyan(f"\n{pet.name} {pet.emoji} : You absolutely killed the joke LOL. Great Job! 🫠"))
        else:
            resp = (answer_expected.capitalize() if answer_expected else "No punchline")
            io.write(cyan(f"\n{pet.name} {pet.emoji} : {resp}! GOT YOU! 🤪"))
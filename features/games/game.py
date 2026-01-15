"""
features/game.py

Game module: business logic coordinator for pet interactions with decoupled I/O and content loading.

Refactor scope (behavior preserved):
- Game is a thin coordinator: delegates menu rendering and topic-type branching.
- Species creation is handled by an injected registry.
- Conversation topic handling is delegated to a TopicHandler registry.
- Actions (Play, Walk, Feed, Bath, Potion) are delegated to specific Action commands.
- Uses a unified IO port (`IOPort`) to avoid `InputPort | OutputPort` mismatch.
- Content loader is injected correctly (no Protocol instantiation).
- Legacy global `User.current_user` access is normalized through an injected UserContext.

Hard constraints:
- No changes to gameplay rules, conditions, outcomes, prompt strings, menu order, or timing.
"""

from __future__ import annotations

import datetime
import json
from random import choice as ch
from typing import Iterable

from constants.configs import LINE, NO_STOCK_MSG
from utils.colorize import red, green, cyan, reset_color
from utils.formatter import Formatter
from utils.ports import ConsoleIO, ContentLoader, IOPort

from features.pet import VirtualPet
from features.actions import BathAction, FeedAction, PlayAction, WalkAction, PotionAction
from .user_context import LegacyUserContext, UserContext
from .species_registry import DefaultSpeciesRegistry, SpeciesRegistry
from .inventory_catalog import DefaultInventoryCatalog, InventoryCatalog
from .topic_handlers import ConversationEngine, FavouriteFoodTopicHandler, MusicTasteTopicHandler
from .game_io_views import GameView


class Game:
    """Main interactive game controller responsible for in-session pet interactions."""

    def __init__(
        self,
        user,
        io: IOPort | None,
        content_loader: ContentLoader,
        species_registry: SpeciesRegistry | None = None,
        user_context: UserContext | None = None,
        inventory_catalog: InventoryCatalog | None = None,
    ):
        self.animal_list = []
        self.clock = datetime.datetime.now().hour
        self.format = Formatter()
        self.spend = 0
        self.day = 0
        self.jokes = []
        self.conversations = []
        self.topics_used = []

        self.io: IOPort = io or ConsoleIO()
        self.user = user

        # Protocols must not be instantiated; callers must inject a concrete loader.
        self.content_loader: ContentLoader = content_loader

        self.species_registry: SpeciesRegistry = species_registry or DefaultSpeciesRegistry()
        self.user_context: UserContext = user_context or LegacyUserContext(self.user)
        self.inventory_catalog: InventoryCatalog = inventory_catalog or DefaultInventoryCatalog()

        self.view = GameView(self.io)
        self._conversation_engine = ConversationEngine(
            io=self.io,
            topics_used=self.topics_used,
            handlers={
                "Music Taste": MusicTasteTopicHandler(io=self.io, user_context=self.user_context),
                "Favourite Food/Drink": FavouriteFoodTopicHandler(io=self.io, user_context=self.user_context),
            },
        )

        self.load_jokes()
        self.load_conversations()

    def load_jokes(self) -> None:
        """Load jokes data through the configured content loader."""
        try:
            self.jokes = self.content_loader.load_json("datas/jokes.json")
        except FileNotFoundError:
            self.io.write(red("Warning: datas/jokes.json not found. Jokes will not be available."))
            self.jokes = []
        except json.JSONDecodeError:
            self.io.write(red("Warning: datas/jokes.json is corrupted. Jokes will not be available."))
            self.jokes = []

    def load_conversations(self) -> None:
        """Load conversation topics through the configured content loader."""
        try:
            self.conversations = self.content_loader.load_json("datas/conversations.json")
        except FileNotFoundError:
            self.io.write(red("Warning: datas/conversations.json not found. Conversations will not be available."))
            self.conversations = []
        except json.JSONDecodeError:
            self.io.write(red("Warning: datas/conversations.json is corrupted. Conversations will not be available."))
            self.conversations = []

    def get_currency(self) -> int:
        return self.user.currency

    def create_name(self) -> tuple[bool, str, str]:
        self.io.write(reset_color("\n" + LINE))
        name = self.io.read("Name your pet: ").title().strip()
        flag, species = self.create_species(name)
        return flag, name, species

    def create_species(self, name: str) -> tuple[bool, VirtualPet | None]:
        """Prompt species selection and create the chosen pet via the injected registry."""
        self.io.write(LINE)
        self.io.write("Here's five types of species you can choose: ")
        self.io.write("1. Cat (🐈)")
        self.io.write("2. Rabbit (🐇)")
        self.io.write("3. Dinosaur (🦖)")
        self.io.write("4. Dragon (🐉)")
        self.io.write("5. Pou (💩)")
        self.io.write(LINE)

        while True:
            species = self.io.read("Choose his/her species (1/2/3/4/5): ").strip()
            animal = self.species_registry.create(species, name, self.io)
            if animal:
                return True, animal
            self.io.write(red("\nUnknown species choice! Please try again.\n"))

    def create(self) -> bool:
        """High-level pet creation flow combining name and species selection."""
        while True:
            flag, name, species = self.create_name()

            if species and flag:
                if not any(animal.name == name for animal in self.user.pets):
                    self.animal_list.append(species)
                    self.io.write(green(f"\nCongratulations! You have successfully give birth to {name}, the {species.type}!"))
                    return True
                self.io.write(red(f"\n{name} has been created! Please create another pet with different name and species.\n"))
                flag = False

            if not flag:
                retry = (
                    self.io.read(
                        "Would you like to create your pet again? (Y/N)\n"
                        "(Note: input other than Y and N will be considered as N): "
                    )
                    .capitalize()
                    .strip()
                )

                if retry == "Y":
                    continue

                self.io.write("")
                return False

    def view(self, pet) -> None:
        """Render a pet's status using the Formatter helper."""
        stats = {
            "name": pet.name,
            "type": pet.type,
            "age": f"{pet.get_age():.1f}",
            "hunger": pet.hunger,
            "fat": pet.fat,
            "sanity": pet.sanity,
            "happiness": pet.happiness,
            "energy": pet.energy,
            "health": pet.health,
            "mood": pet.get_mood(),
            "summary": pet.get_summary(),
            "age_summary": pet.get_age_summary(),
        }
        self.io.write(self.format.format_status_box(stats))

    @staticmethod
    def get_health(pet) -> int:
        return pet.health

    @staticmethod
    def _render_lines(items: Iterable[str]) -> str:
        return "\n".join(items)

    @staticmethod
    def _input_int(prompt: str, reader: IOPort):
        try:
            return int(reader.read(prompt))
        except ValueError:
            return None

    def _print_stock(self, title: str, defs: dict, category: str) -> None:
        lines = ["", LINE, title, LINE + "\n"]
        inv = self.user.inventory[category]
        is_food = category == "food"
        is_soap = category == "soap"

        for idx, (key, v) in enumerate(defs.items(), start=1):
            emoji = str(v["emoji"])
            qty = inv.get(key, 0)
            stock_text = f"{qty}" if qty > 0 else f"{red(NO_STOCK_MSG)}"
            if is_food:
                lines.append(
                    f"{idx}. {key} {emoji} (Hunger: {v['hunger']}, Happiness: {v['happiness']}, Available: {stock_text})"
                )
            elif is_soap:
                lines.append(
                    f"{idx}. {key} {emoji} (Sanity: {v['sanity']}, Happiness: {v['happiness']}, Available: {stock_text})"
                )
            else:
                lines.append(f"{idx}. {key} {emoji} (Available: {stock_text}, Effect: {v['delta']})")
        self.io.write("\n".join(lines))

    def _feed(self, pet: VirtualPet) -> None:
       action = FeedAction(self.inventory_catalog)
       action.execute(pet, self.user, self.io)

    def _play(self, self_pet: VirtualPet) -> None:
        action = PlayAction()
        action.execute(self_pet, self.user, self.io)
        
    def _bath(self, pet: VirtualPet) -> None:
        action = BathAction(self.inventory_catalog)
        action.execute(pet, self.user, self.io)

    def _action_potion(self, pet: VirtualPet) -> None:
        action = PotionAction(self.inventory_catalog)
        action.execute(pet, self.user, self.io)

    def _sleep(self, pet: VirtualPet) -> None:
        hours = self._input_int(f"\n{pet.name}'s sleep duration (1-12): ", self.io)

        if hours is None:
            self.io.write(red("\nPlease insert digit at choice input!\n"))
            return
        if not (1 <= hours <= 12):
            self.io.write(red("\nSleep duration must between 1 to 12 hours.\n"))
            return

        pet.sleep(hours)

    def _walk(self, self_pet: VirtualPet) -> None:
        action = WalkAction()
        action.execute(self_pet, self.user, self.io)

    def _topic_plan(self, pet: VirtualPet) -> bool:
        ans = [
            f"I want to eat {pet.fav_food}!",
            "I want to play :D",
            "I want to take a walk 🌳.",
            "I want to take a bath :)",
            "I want to talk to you..👉👈",
        ]
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : {ch(ans)}"))
        return True

    def _topic_fav_food(self, pet: VirtualPet) -> bool:
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : My favourite food is {pet.fav_food}. :D"))
        return True

    def _topic_money(self, pet: VirtualPet) -> bool:
        if all(val < 50 for val in [pet.hunger, pet.sanity, pet.happiness, pet.health]):
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I will consider it if you take care of me properly!\n"))
            return False

        if pet.generosity < 2:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Here, I'll give you Rp. 100,000."))
            self.user.currency += 100000
            pet.generosity += 1
            return True

        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Sorry, can't give you anymore... 😔\n"))
        return False

    def _end_topic(self, pet: VirtualPet) -> None:
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Okay, I have gotten to know you more, thanks for sharing yours!"))
        self.io.write(green(f"{pet.name}'s happiness has increased by 10."))
        pet.happiness += 10

    def _music_topic(self, pet: VirtualPet) -> bool:
        if not self.conversations:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!"))
            return False

        music_questions = [q for q in self.conversations if q.get("type") == "Music Taste"]
        if not music_questions:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I don't have any music topics right now! Sorry!"))
            return False

        return self._conversation_engine.handle_random_topic_of_type(pet, self.conversations, "Music Taste")

    def _food_topic(self, pet: VirtualPet) -> bool:
        if not self.conversations:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!"))
            return False

        food_questions = [q for q in self.conversations if q.get("type") == "Favourite Food/Drink"]
        if not food_questions:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I don't have any food topics right now! Sorry!"))
            return False

        return self._conversation_engine.handle_random_topic_of_type(pet, self.conversations, "Favourite Food/Drink")

    def _topic_conversation_menu(self, pet: VirtualPet) -> bool:
        while True:
            self.view.print_conversation_menu()
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : What would you like to talk today? "))
            topic = self._input_int("Choose a topic: ", self.io)
            if topic is None:
                self.io.write(red("\nPlease type a number."))
                continue

            actions = {1: self._music_topic, 2: self._food_topic, 3: self._end_topic}
            keep_talking = actions.get(topic, self._invalid_topic)(pet)
            if keep_talking is None:
                break
        return True

    def _can_tell_joke(self, pet: VirtualPet) -> tuple[bool, str | None]:
        if pet.hunger < 30:
            return False, f"\n{pet.name} is too hungry to joke right now.."
        if pet.health < 20:
            return False, f"\n{pet.name} is too sick to joke right now.."
        if pet.energy < 10:
            return False, f"\n{pet.name} is too tired to joke right now.."
        if pet.happiness < 20:
            return False, f"\n{pet.name} is too stressed to joke right now.."
        return True, None

    def _topic_joke(self, pet: VirtualPet) -> bool:
        ok, reason = self._can_tell_joke(pet)
        if not ok:
            self.io.write(red(reason + "\n"))
            return False

        if not self.jokes:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of jokes right now! Sorry!"))
            return True

        random_jokes = ch(self.jokes)
        question = random_jokes.get("question", "")
        answer_expected = random_jokes.get("answer", "")
        ans = self.io.read(cyan(f"\n{pet.name} {pet.emoji} : {question} ")).strip()

        if ans.lower() == (answer_expected or "").lower():
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Wait! How did you know? 😱"))
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : You absolutely killed the joke LOL. Great Job! 🫠"))
        else:
            resp = (answer_expected.capitalize() if answer_expected else "No punchline")
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : {resp}! GOT YOU! 🤪"))
        return True

    def _topic_goodbye(self, pet: VirtualPet) -> bool:
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Okay, goodbye!"))
        self.io.write(green(f"{pet.name}'s happiness has increased by 10.\n"))
        pet.happiness += 10
        return False

    def _invalid_topic(self, *_args, **_kwargs) -> bool:
        self.io.write(red("\nPlease choose based on choices we have!"))
        return True

    def _talk_menu(self, pet: VirtualPet) -> None:
        while True:
            self.view.print_talk_menu()
            topic = self._input_int("Choose a topic: ", self.io)
            if topic is None:
                self.io.write(red("\nPlease type a number."))
                continue

            actions = {
                1: self._topic_plan,
                2: self._topic_fav_food,
                3: self._topic_conversation_menu,
                4: self._topic_money,
                5: self._topic_joke,
                6: self._topic_goodbye,
            }
            action = actions.get(topic)
            if action is None:
                self._invalid_topic()
                continue

            keep_talking = action(pet)
            if not keep_talking:
                break

    def _stocks(self) -> dict:
        return {
            1: ["List of Foods:", self.inventory_catalog.food_defs(), "food"],
            3: ["List of Soaps:", self.inventory_catalog.soap_defs(), "soap"],
            4: ["List of Potions:", self.inventory_catalog.potion_defs(), "potion"],
        }

    def _actions(self):
        return {
            1: self._feed,
            2: self._play,
            3: self._bath,
            4: self._action_potion,
            5: self._sleep,
            6: self._walk,
            7: self._talk_menu,
        }

    @staticmethod
    def _is_valid_choice(choice: int) -> bool:
        return 1 <= choice <= 8

    def _should_show_stock(self, choice: int) -> bool:
        return choice in self._stocks()

    def interact(self, pet) -> None:
        self.io.write(reset_color("\n" + "=" * 120))
        self.io.write(f"Playing with {pet.name}, the {pet.type}:".center(len(LINE)))
        while True:
            self.view.print_main_interact_menu()
            choice = self._input_int("Choose (1-8): ", self.io)

            if choice is None:
                self.io.write(red("\nPlease enter digit!\n"))
                continue

            if (choice == 8) or (pet.health == 0):
                self.io.write("")
                break

            if not self._is_valid_choice(choice):
                self.io.write(red("\nPlease choose from (1-8).\n"))
                continue

            if self._should_show_stock(choice):
                title, defs, category = self._stocks()[choice]
                self._print_stock(title, defs, category)

            action = self._actions().get(choice)
            if action:
                action(pet)
"""
features/game.py

Game module: business logic coordinator.

Refactor Status:
- ✅ SRP: UI and Action logic removed.
- ✅ OCP: Actions are injected via list; new actions can be added without changing this file.
- ✅ DIP: Depends on abstractions (IOPort, PetAction).
"""

from __future__ import annotations

import datetime
import json
from typing import List

from constants.configs import UIConfig as UIC
from utils.colorize import red, green, reset_color
from utils.formatter import Formatter
from utils.ports import ConsoleIO, ContentLoader, IOPort

from features.pet import VirtualPet
from features.actions import (
    PetAction, FeedAction, PlayAction, BathAction, 
    PotionAction, SleepAction, WalkAction, TalkAction
)
from .user_context import LegacyUserContext, UserContext
from .species_registry import DefaultSpeciesRegistry, SpeciesRegistry
from .inventory_catalog import DefaultInventoryCatalog, InventoryCatalog
from .topic_handlers import ConversationEngine, FavouriteFoodTopicHandler, MusicTasteTopicHandler
from .game_io_views import GameView


class Game:
    """Main interactive game coordinator."""

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
        
        self.io: IOPort = io or ConsoleIO()
        self.user = user
        self.content_loader: ContentLoader = content_loader
        self.species_registry = species_registry or DefaultSpeciesRegistry()
        self.user_context = user_context or LegacyUserContext(self.user)
        self.inventory_catalog = inventory_catalog or DefaultInventoryCatalog()
        self.view = GameView(self.io)

        self.jokes = self._load_json_safe("datas/jokes.json", "Jokes")
        self.conversations = self._load_json_safe("datas/conversations.json", "Conversations")
        self.topics_used = []

        self._conversation_engine = ConversationEngine(
            io=self.io,
            topics_used=self.topics_used,
            handlers={
                "Music Taste": MusicTasteTopicHandler(io=self.io, user_context=self.user_context),
                "Favourite Food/Drink": FavouriteFoodTopicHandler(io=self.io, user_context=self.user_context),
            },
        )

        self.actions: List[PetAction] = [
            FeedAction(self.inventory_catalog),
            PlayAction(),
            BathAction(self.inventory_catalog),
            PotionAction(self.inventory_catalog, self.view),
            SleepAction(),
            WalkAction(),
            TalkAction(self._conversation_engine, self.view, self.jokes, self.conversations)
        ]
        

    def _load_json_safe(self, path: str, name: str) -> list:
        try:
            return self.content_loader.load_json(path)
        except (FileNotFoundError, json.JSONDecodeError):
            self.io.write(red(f"Warning: {name} unavailable (file missing or corrupt)."))
            return []

    def get_currency(self) -> int:
        return self.user.currency

    def create_name(self) -> tuple[bool, str, str]:
        self.io.write(reset_color("\n" + UIC.LINE))
        name = self.io.read("Name your pet: ").title().strip()
        flag, species = self.create_species(name)
        return flag, name, species

    def create_species(self, name: str) -> tuple[bool, VirtualPet | None]:
        self.io.write(UIC.LINE)
        self.io.write("Here's five types of species you can choose: ")
        self.io.write("1. Cat (🐈)")
        self.io.write("2. Rabbit (🐇)")
        self.io.write("3. Dinosaur (🦖)")
        self.io.write("4. Dragon (🐉)")
        self.io.write("5. Pou (💩)")
        self.io.write(UIC.LINE)

        while True:
            species = self.io.read("Choose his/her species (1/2/3/4/5): ").strip()
            animal = self.species_registry.create(species, name, self.io)
            if animal:
                return True, animal
            self.io.write(red("\nUnknown species choice! Please try again.\n"))

    def create(self) -> bool:
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

    def interact(self, pet: VirtualPet) -> None:
        """
        Main interaction loop. 
        Dynamically renders menu based on self.actions list.
        """
        self.io.write(reset_color("\n" + "=" * 120))
        self.io.write(f"Playing with {pet.name}, the {pet.type}:".center(len(UIC.LINE)))
        
        while True:
            # 1. Render Menu Dynamically
            self.io.write(UIC.LINE)
            for idx, action in enumerate(self.actions, start=1):
                self.io.write(f"{idx}. {action.menu_name}")
            
            exit_idx = len(self.actions) + 1
            self.io.write(f"{exit_idx}. Exit")
            self.io.write(UIC.LINE)

            # 2. Get Input
            try:
                choice = int(self.io.read(f"Choose (1-{exit_idx}): "))
            except ValueError:
                self.io.write(red("\nPlease enter a digit!\n"))
                continue

            # 3. Handle Exit
            if choice == exit_idx or pet.health == 0:
                self.io.write("")
                break

            # 4. Dispatch to Action
            # Array index is choice - 1
            if 1 <= choice <= len(self.actions):
                action = self.actions[choice - 1]
                action.execute(pet, self.user, self.io)
            else:
                self.io.write(red(f"\nPlease choose from (1-{exit_idx}).\n"))
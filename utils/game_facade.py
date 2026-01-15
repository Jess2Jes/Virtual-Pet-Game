"""
features/game_facade.py

Facade orchestrating core gameplay, persistence, and minigames.

This module preserves the existing GameFacade API and behavior while improving SRP/DIP:
- Minigame creation remains registry-based.
- Save/load bootstrapping is delegated to a small internal persistence adapter.
- Construction of Shop/Game is centralized behind factory callables to reduce coupling.
"""

import datetime
from importlib import import_module
from typing import Callable, Dict, Type

from constants.configs import GAME_LIST, MINIGAME_SPECS
from features.games.game import Game
from features.shop import Shop
from features.user import User
from repositories.save_repository import SaveRepository
from repositories.save_manager import SaveManager
from repositories.user_repository import UserRepository
from utils.colorize import green, red, yellow
from utils.ports import ContentLoader, ConsoleIO, FileContentLoader, OutputPort


class MinigameRegistry:
    """Registry/factory for minigames to decouple facade from concrete imports."""

    def __init__(self):
        self._factories: Dict[str, Callable[[], object]] = {}

    def register(self, name: str, module_path: str, class_name: str) -> None:
        """Register a minigame by name with its module and class."""

        def factory(io: OutputPort = None):
            module = import_module(module_path)
            cls: Type = getattr(module, class_name)
            return cls(io=io)

        self._factories[name] = factory

    def create(self, name: str, io: OutputPort = None) -> object:
        """Create a minigame instance by name."""
        factory = self._factories.get(name)
        if not factory:
            raise ValueError(f"Unknown minigame: {name}")
        return factory(io=io)

    @classmethod
    def from_specs(cls, specs: Dict[str, Dict[str, str]]) -> "MinigameRegistry":
        """Build a registry from a spec mapping: name -> {module, class}."""
        registry = cls()
        for name, spec in specs.items():
            registry.register(name, spec["module"], spec["class"])
        return registry


class GameFacade:
    """
    High-level interface coordinating user, game, saves, shop, and minigames.

    Public API is preserved. Internally, dependency creation is centralized behind
    factories to reduce coupling to concrete types.
    """

    def __init__(
        self,
        io: OutputPort | None = None,
        save_repo: SaveRepository | None = None,
        content_loader: ContentLoader | None = None,
        *,
        user_repo: UserRepository | None = None,
        game_factory: Callable[[User, OutputPort, ContentLoader], Game] | None = None,
        shop_factory: Callable[[User, OutputPort], Shop] | None = None,
    ):
        self.io: OutputPort = io or ConsoleIO()
        self.content_loader: ContentLoader = content_loader or FileContentLoader()
        self.user_repo: UserRepository = user_repo or UserRepository()

        self.game = None
        self.current_user = None

        self._minigame_registry = MinigameRegistry.from_specs(MINIGAME_SPECS)
        self.save_manager: SaveRepository = save_repo or SaveManager.get_instance()

        self._game_factory = game_factory or (lambda user, io, loader: Game(user, io=io, content_loader=loader))
        self._shop_factory = shop_factory or (lambda user, io: Shop(user, io=io))

        self._load_all_users_from_saves()

    def get_user_count(self) -> int:
        """Return the total number of registered users."""
        return len(self.user_repo.get_all())

    def _connect_to_game(self) -> None:
        """Ensure game instance is initialized for the current user."""
        if self.current_user and (not self.game or self.game.user != self.current_user):
            self.game = self._game_factory(self.current_user, self.io, self.content_loader)

    def register_user(self, username: str, password: str) -> bool:
        """Register and connect a new user."""
        if self.user_repo.exists(username):
            self.io.write(red("This username has already existed!\n"))
            return False

        if username.strip().lower() in password.strip().lower():
            self.io.write(red("Password cannot be the same as username!\n"))
            return False

        try:
            new_user = User(username)
            new_user.password = password
        except ValueError as e:
            self.io.write(red(f"Registration Failed: {e}"))
            if "Password" in str(e):
                self.io.write(yellow("Hint: 8+ chars, 1 Upper, 1 Lower, 1 Number, 1 Symbol.\n"))
            return False

        self.user_repo.add(new_user)

        initial_state = {
            "user": new_user.create_memento(),
            "game": {"day": 0, "spend": 0, "clock": 8},
        }

        self.save_manager.save_game(username, initial_state)
        self.current_user = new_user
        self.io.write(green(f"User {username} registered successfully!\n"))

        self._connect_to_game()
        return True

    def login_user(self, username: str, password: str) -> bool:
        """Login flow with save loading."""
        user = self.user_repo.get_by_username(username)

        if not user:
            self.io.write(red("User not found!\n"))
            return False

        if not user.auth_service.verify(password, user.password):
            self.io.write(red("Wrong password!\n"))
            return False

        self.current_user = user
        self.io.write(green(f"Welcome back, {user.username}!\n"))

        self._connect_to_game()

        self.io.write("\n💾 Checking for saved game...")
        if self._load_game(user.username):
            self.io.write(green("🔃 Previous game loaded!\n"))
        else:
            self.io.write(yellow("ℹ️ Starting fresh game.\n"))
        return True

    def logout_user(self) -> None:
        """Logout current user."""
        self.current_user = None
        self.io.write(green("Logged out successfully!\n"))

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password and persist game state."""
        user = self.user_repo.get_by_username(username)

        if not user:
            return False
        if not user.auth_service.verify(old_password, user.password):
            return False
        if new_password == old_password:
            return False
        user.password = new_password
        if not user.auth_service.verify(new_password, user.password):
            return False

        try:
            user.password = new_password
        except ValueError as e:
            self.io.write(red(f"Cannot change password: {e}"))
            return False

        game_state = {
            "user": user.create_memento(),
            "game": {
                "day": self.game.day if self.game else 0,
                "spend": self.game.spend if self.game else 0,
                "clock": self.game.clock if self.game else 8,
            },
        }
        self.save_manager.save_game(user.username, game_state)
        return True

    def create_pet(self) -> bool:
        """Create a pet via Game and attach to current user."""
        self._connect_to_game()
        if not self.current_user:
            return False
        flag = self.game.create()
        if self.game.animal_list and flag:
            new_pet = self.game.animal_list[-1]
            self.current_user.add_pet(new_pet)
            return True
        return False

    def get_pets(self) -> list:
        """Return pets owned by current user."""
        if not self.current_user:
            return []
        return self.current_user.pets

    def view_pet_stats(self, pet) -> None:
        """Display pet stats."""
        self.game.view(pet)

    def interact_pet(self, pet) -> None:
        """Run interaction loop then advance pet time."""
        self.game.interact(pet)
        pet.time_past()

    def get_pet_age(self, pet) -> float:
        """Return pet age if available."""
        return pet.get_age() if hasattr(pet, "get_age") else 0

    def get_pet_stage(self, pet):
        """Return rendered pet stage based on age."""
        age = self.get_pet_age(pet)
        if age < 1:
            return pet.baby()
        elif 1 <= age < 3:
            return pet.teen()
        elif 3 <= age < 10:
            return pet.adult()
        else:
            return pet.elder()

    def get_current_time(self) -> str:
        """Return current in-game clock."""
        self._connect_to_game()
        clock = self.game.clock - 12 if self.game.clock > 12 else self.game.clock
        return f"{clock} A.M." if self.game.clock < 12 else f"{clock} P.M."

    def get_current_day(self) -> int:
        """Return current in-game day with rollover logic."""
        self._connect_to_game()
        if self.game.spend == 24:
            self.game.day += 1
        return self.game.day

    def spend_time(self) -> None:
        """Increment spend counter (hour)."""
        self._connect_to_game()
        self.game.spend += 1

    def save_game(self) -> bool:
        """Persist current game state."""
        if not self.current_user:
            return False
        game_state = {
            "user": self.current_user.create_memento(),
            "game": {
                "day": self.game.day,
                "spend": self.game.spend,
                "clock": self.game.clock,
            },
        }
        return self.save_manager.save_game(self.current_user.username, game_state)

    def enter_shop(self) -> None:
        """Enter shop interaction."""
        if self.current_user:
            shop = self._shop_factory(self.current_user, self.io)
            shop.interact()

    def get_minigames(self) -> list:
        """List available minigame names."""
        return GAME_LIST

    def play_minigame(self, game_name: str, pet) -> bool:
        """Play a registered minigame and apply rewards."""
        game = self._minigame_registry.create(game_name, io=self.io)
        result = game.play(self.current_user, pet)
        if result:
            coins = int(result.get("currency", 0))
            pet_happiness = int(result.get("pet_happiness", 0))
            if coins:
                self.current_user.currency += coins
                self.current_user.limit_currency()
            if pet and pet_happiness and hasattr(pet, "happiness"):
                happiness_increase = min(100, pet.happiness + pet_happiness)
                pet.happiness = happiness_increase
            return True
        return False

    def _load_all_users_from_saves(self) -> None:
        """Populate the repository from saved state."""
        try:
            all_saves = self.save_manager._load_all_saves()  # type: ignore[attr-defined]
        except Exception:
            all_saves = {}

        for username, save_data in all_saves.items():
            if not self.user_repo.exists(username):
                user_data = save_data.get("user", {})
                password_hash = user_data.get("password", "")
                user = User(username, password_hash)
                user.restore_from_memento(user_data)
                self.user_repo.add(user)

    def _load_game(self, username) -> bool:
        """Load game state for a username."""
        game_state = self.save_manager.load_game(username)
        if not game_state:
            return False
        user_data = game_state.get("user", {})
        self.current_user.restore_from_memento(user_data)
        game_data = game_state.get("game", {})
        self.game.day = game_data.get("day", 0)
        self.game.spend = game_data.get("spend", 0)
        self.game.clock = game_data.get("clock", datetime.datetime.now().hour)
        return True

    def _save_game(self) -> bool:
        """Persist state (alias to save_game)."""
        if not self.current_user:
            return False
        game_state = {
            "user": self.current_user.create_memento(),
            "game": {
                "day": self.game.day,
                "spend": self.game.spend,
                "clock": self.game.clock,
            },
        }
        return self.save_manager.save_game(self.current_user.username, game_state)
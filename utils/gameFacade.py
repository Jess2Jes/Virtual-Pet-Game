"""Facade orchestrating game subsystems with a registry-based minigame factory."""

import datetime
from importlib import import_module
from typing import Callable, Dict, Type

from features.shop import Shop
from features.game import Game
from features.save_manager import SaveManager
from features.user import User
from utils.colorize import green, yellow
from constants.configs import GAME_LIST


class MinigameRegistry:
    """Registry/factory for minigames to decouple facade from concrete imports."""
    def __init__(self):
        self._factories: Dict[str, Callable[[], object]] = {}

    def register(self, name: str, module_path: str, class_name: str):
        """Register a minigame by name with its module and class."""
        def factory():
            module = import_module(module_path)
            cls: Type = getattr(module, class_name)
            return cls()
        self._factories[name] = factory

    def create(self, name: str):
        """Create a minigame instance by name."""
        factory = self._factories.get(name)
        if not factory:
            raise ValueError(f"Unknown minigame: {name}")
        return factory()


class GameFacade:
    """High-level interface coordinating user, game, saves, shop, and minigames."""
    def __init__(self):
        self.game = None
        self.current_user = User.current_user
        self.save_manager = SaveManager.get_instance()
        self._minigame_registry = self._init_minigame_registry()
        self._load_all_users_from_saves()

    @staticmethod
    def _init_minigame_registry() -> MinigameRegistry:
        """Initialize registry with available minigames."""
        registry = MinigameRegistry()
        registry.register("Math Quiz", "features.minigame.mathQuiz", "MathQuiz")
        registry.register("Tic Tac Toe", "features.minigame.ticTacToe", "TicTacToe")
        registry.register("Memory Match", "features.minigame.memoryMatch", "MemoryMatch")
        registry.register("Battle Contest", "features.minigame.battleContest", "BattleContest")
        registry.register("Sudoku", "features.minigame.sudoku", "Sudoku")
        registry.register("Tetris", "features.minigame.tetris", "Tetris")
        registry.register("Uno", "features.minigame.uno", "Uno")
        return registry

    def _connect_to_game(self):
        """Ensure game instance is initialized for the current user."""
        if self.current_user and (not self.game or self.game.user != self.current_user):
            self.game = Game(self.current_user)

    def register_user(self, username: str, password: str) -> bool:
        """Register and connect a new user."""
        auth = User.register(username, password)
        if auth is not None:
            self.current_user = User.current_user
            self._connect_to_game()
            return True
        return False

    def login_user(self, username: str, password: str) -> bool:
        """Login flow with save loading."""
        auth = User.login(username, password)
        if auth is not None:
            self.current_user = User.current_user
            self._connect_to_game()
            print("\n💾 Checking for saved game...")
            if self._load_game(username):
                print(green("🔃 Previous game loaded!\n"))
            else:
                print(yellow("ℹ️ Starting fresh game.\n"))
            return True
        return False

    def logout_user(self) -> None:
        """Logout current user."""
        User._logout()
        self.current_user = User.current_user

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password and persist game state."""
        key = username.casefold()
        if key not in User.users:
            return False
        user = User.users[key]
        if not User._check_password(old_password, user.password):
            return False
        if new_password == old_password:
            return False
        user.password = new_password
        if not User._check_password(new_password, user.password):
            return False
        game_state = {
            "user": user.create_memento(),
            "game": {
                "day": self.game.day,
                "spend": self.game.spend,
                "clock": self.game.clock,
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
            shop = Shop(self.current_user)
            shop.interact()

    def get_minigames(self) -> list:
        """List available minigame names."""
        return GAME_LIST

    def play_minigame(self, game_name: str, pet) -> bool:
        """Play a registered minigame and apply rewards."""
        game = self._minigame_registry.create(game_name)
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

    def _load_all_users_from_saves(self):
        """Load all saved users into in-memory registry."""
        try:
            all_saves = self.save_manager._load_all_saves()
        except Exception:
            all_saves = {}
        for username, save_data in all_saves.items():
            key = username.casefold()
            if key not in User.users:
                user_data = save_data.get("user", {})
                password_hash = user_data.get("password", "")
                user = User(username, password_hash)
                user.restore_from_memento(user_data)
                User.users[key] = user

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
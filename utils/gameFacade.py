import datetime
from features.shop import Shop
from features.game import Game
from features.save_manager import SaveManager
from features.user import User
from utils.colorize import green, yellow
from constants.configs import GAME_LIST

class GameFacade:
    """
    Facade that coordinates game subsystems (game logic, users, minigames, persistence).

    Changes:
    - Minigame engine is created lazily on first use to avoid heavy imports at startup.
    """
    def __init__(self):
        self.game = None
        self.current_user = User.current_user
        self.save_manager = SaveManager.get_instance()
        # Load saved users into in-memory registry so players can log in later
        self._load_all_users_from_saves()

    def _connect_to_game(self):
        if self.current_user and (not self.game or self.game.user != self.current_user):
            self.game = Game(self.current_user)

    def register_user(self, username: str, password: str) -> bool:
        auth = User.register(username, password)
        if auth is not None:
            self.current_user = User.current_user
            self._connect_to_game()
            return True
        return False

    def login_user(self, username: str, password: str) -> bool:
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
        User._logout()
        self.current_user = User.current_user

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
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

    # === Pet Management ===
    def create_pet(self) -> bool:
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
        if not self.current_user:
            return []
        return self.current_user.pets

    def view_pet_stats(self, pet) -> None:
        self.game.view(pet)

    def interact_pet(self, pet) -> None:
        self.game.interact(pet)
        pet.time_past()

    def get_pet_age(self, pet) -> float:
        return pet.get_age() if hasattr(pet, "get_age") else 0

    def get_pet_stage(self, pet):
        age = self.get_pet_age(pet)
        if age < 1:
            return pet.baby()
        elif 1 <= age < 3:
            return pet.teen()
        elif 3 <= age < 10:
            return pet.adult()
        else:
            return pet.elder()

    # === Game State Management ===
    def get_current_time(self) -> str:
        self._connect_to_game()
        clock = self.game.clock - 12 if self.game.clock > 12 else self.game.clock
        return f"{clock} A.M." if self.game.clock < 12 else f"{clock} P.M."

    def get_current_day(self) -> int:
        self._connect_to_game()
        if self.game.spend == 24:
            self.game.day += 1
        return self.game.day

    def spend_time(self) -> None:
        self._connect_to_game()
        self.game.spend += 1

    def save_game(self) -> bool:
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
        if self.current_user:
            shop = Shop(self.current_user)
            shop.interact()

    def get_minigames(self) -> list:
        return GAME_LIST

    def play_minigame(self, game_name: str, pet) -> bool:

        if game_name == "Math Quiz":
            from features.minigame.mathQuiz import MathQuiz
            game = MathQuiz()
        elif game_name == "Tic Tac Toe":
            from features.minigame.ticTacToe import TicTacToe
            game = TicTacToe()
        elif game_name == "Memory Match":
            from features.minigame.memoryMatch import MemoryMatch
            game = MemoryMatch()
        elif game_name == "Battle Contest":
            from features.minigame.battleContest import BattleContest
            game = BattleContest()
        elif game_name == "Sudoku":
            from features.minigame.sudoku import Sudoku
            game = Sudoku()
        elif game_name == "Tetris":
            from features.minigame.tetris import Tetris
            game = Tetris()
        elif game_name == "Uno":
            from features.minigame.uno import Uno
            game = Uno()

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

    # === Private Methods ===
    def _load_all_users_from_saves(self):
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
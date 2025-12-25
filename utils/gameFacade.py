import datetime
from features.shop import Shop
from features.game import Game
from features.minigame import engine
from features.save_manager import SaveManager
from features.user import User
from utils.colorize import green, yellow

class GameFacade:
    """
    Facade that coordinates game subsystems (game logic, users, minigames, persistence).

    The facade reduces coupling between the CLI (Main) and internal modules by
    exposing a small set of methods the UI can call.
    """

    def __init__(self):
        self.game = Game()
        self.current_user = User.current_user
        self._minigame_engine = engine()
        self.save_manager = SaveManager.get_instance()
        # Load saved users into in-memory registry so players can log in later
        self._load_all_users_from_saves()

    # === User Management ===
    def register_user(self, username: str, password: str) -> bool:
        """Register a new user and set them as the current user on success."""
        auth = User.register(username, password)
        if auth is not None:
            self.current_user = User.current_user
            return True
        return False

    def login_user(self, username: str, password: str) -> bool:
        """Authenticate a user and load a saved game if one exists."""
        auth = User.login(username, password)
        if auth is not None:
            self.current_user = User.current_user
            print("\n💾 Checking for saved game...")
            if self._load_game(username):
                print(green("🔃 Previous game loaded!\n"))
            else:
                print(yellow("ℹ️ Starting fresh game.\n"))
            return True
        return False

    def logout_user(self) -> None:
        """Log out the current user and clear facade state."""
        User._logout()
        self.current_user = User.current_user

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change an existing user's password and persist the updated save.

        Returns True when the password change and save were successful.
        """
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
        """Run the pet creation flow and attach the newly created pet to the current user."""
        if not self.current_user:
            return False

        flag = self.game.create()
        if self.game.animal_list and flag:
            new_pet = self.game.animal_list[-1]
            self.current_user.add_pet(new_pet)
            return True
        return False

    def get_pets(self) -> list:
        """Return the list of pets belonging to the current user (or empty list)."""
        if not self.current_user:
            return []
        return self.current_user.pets

    def view_pet_stats(self, pet) -> None:
        """Render a pet's stats using the Game helper."""
        self.game.view(pet)

    def interact_pet(self, pet, user) -> None:
        """Enter the interactive play loop for a pet and then advance time for the pet."""
        self.game.interact(pet, user)
        pet.time_past()

    def get_pet_age(self, pet) -> float:
        """Return a pet's age (defensive: if method missing, return 0)."""
        return pet.get_age() if hasattr(pet, "get_age") else 0

    def get_pet_stage(self, pet):
        """
        Helper to obtain a pet's life-stage generator/iterator.

        The pet implementation is expected to provide methods like baby()/teen()/adult()/elder()
        that produce a sequence (possibly asynchronous) describing the stage. The facade simply
        selects which method to call based on age.
        """
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
        """
        Human-friendly current time string derived from the game's internal clock (hour).
        Uses a simple 12-hour format with A.M./P.M. labels.
        """
        clock = self.game.clock - 12 if self.game.clock > 12 else self.game.clock
        return f"{clock} A.M." if self.game.clock < 12 else f"{clock} P.M."

    def get_current_day(self) -> int:
        """
        Return the current in-game day. If spending reached 24 hours, increment day.

        Note: spend reset logic is handled elsewhere in the game loop (if needed).
        """
        if self.game.spend == 24:
            self.game.day += 1
        return self.game.day

    def spend_time(self) -> None:
        """Increment the game's spend counter (used to track time progression)."""
        self.game.spend += 1

    def save_game(self) -> bool:
        """Persist the current user's game state via the SaveManager."""
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

    # === Shop Management ===
    def enter_shop(self) -> None:
        """Open the shop UI for the current user (blocking interactive flow)."""
        if self.current_user:
            shop = Shop(self.current_user)
            shop.interact()

    # === Minigames Management ===
    def get_minigames(self) -> list:
        """Return a list of registered minigame names available to play."""
        return self._minigame_engine.list_games()

    def play_minigame(self, game_name: str, pet) -> bool:
        """
        Play a named minigame with the current user and specified pet.

        Applies currency and happiness rewards to the user/pet when the minigame returns a result.
        """
        result = self._minigame_engine.play(game_name, self.current_user, pet)

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
        """Load saved users from disk into the in-memory User registry at startup."""
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


    def _load_game(self, username: str) -> bool:
        """Load a specific user's saved game state (user+game) and restore it into memory."""
        game_state = self.save_manager.load_game(self.current_user.username)

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
        """Convenience wrapper around save_game that uses the facade's current user."""
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
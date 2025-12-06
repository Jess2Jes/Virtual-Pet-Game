from features.shop import Shop
from features.game import Game
from features.user import User, loading
import sys
from features.formatter import GARIS
from features.minigame import engine
import os
import datetime
from features.save_manager import SaveManager
import asyncio
from colorama import Fore, init

init(autoreset=True)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

INPUT_USERNAME = "Username: "
INPUT_PASSWORD = "Password: "


class GameFacade:
    def __init__(self):
        self.game = Game()
        self.current_user = User.current_user
        self._minigame_engine = engine()
        self.save_manager = SaveManager.get_instance()
        self._load_all_users_from_saves()

    # === User Management ===
    def register_user(self, username: str, password: str) -> bool:
        auth = User.register(username, password)
        if auth is not None:
            self.current_user = User.current_user
            return True
        return False

    def login_user(self, username: str, password: str) -> bool:
        auth = User.login(username, password)
        if auth is not None:
            self.current_user = User.current_user
            print("\n💾 Checking for saved game...")
            if self._load_game(username):
                print(Fore.GREEN + "✅ Previous game loaded!\n")
            else:
                print(Fore.YELLOW + "ℹ️ Starting fresh game.\n")
            return True
        return False

    def logout_user(self) -> None:
        User._logout()
        self.current_user = User.current_user

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        if username not in User.users:
            return False

        user = User.users[username]

        if not User._check_password(old_password, user.password):
            return False

        if new_password == old_password:
            return False

        user.password = new_password

        if not User._check_password(new_password, user.password):
            return False

        game_state = {
            'user': user.create_memento(),
            'game': {
                'day': self.game.day,
                'spend': self.game.spend,
                'clock': self.game.clock
            }
        }

        self.save_manager.save_game(user.username, game_state)

        return True

    # === Pet Management ===
    def create_pet(self) -> bool:
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

    def interact_pet(self, pet, user) -> None:
        self.game.interact(pet, user)
        pet.time_past()

    def get_pet_age(self, pet) -> float:
        return pet.get_age() if hasattr(pet, 'get_age') else 0

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
        clock = self.game.clock - 12 if self.game.clock > 12 else self.game.clock
        return f"{clock} A.M." if self.game.clock < 12 else f"{clock} P.M."

    def get_current_day(self) -> int:
        if self.game.spend == 24:
            self.game.day += 1
        return self.game.day

    def spend_time(self) -> None:
        self.game.spend += 1

    def save_game(self) -> bool:
        if not self.current_user:
            return False

        game_state = {
            'user': self.current_user.create_memento(),
            'game': {
                'day': self.game.day,
                'spend': self.game.spend,
                'clock': self.game.clock
            }
        }
        return self.save_manager.save_game(self.current_user.username, game_state)

    # === Shop Management ===
    def enter_shop(self) -> None:
        if self.current_user:
            shop = Shop(self.current_user)
            shop.interact()

    # === Minigames Management ===
    def get_minigames(self) -> list:
        return self._minigame_engine.list_games()

    def play_minigame(self, game_name: str, pet) -> bool:
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
        try:
            all_saves = self.save_manager._load_all_saves()
        except Exception:
            all_saves = {}

        for username, save_data in all_saves.items():
            if username not in User.users:
                user_data = save_data.get('user', {})
                password_hash = user_data.get('password', '')

                user = User(username, password_hash)
                user.restore_from_memento(user_data)

                User.users[username] = user

    def _load_game(self, username: str) -> bool:
        game_state = self.save_manager.load_game(username)

        if not game_state:
            return False

        user_data = game_state.get('user', {})
        self.current_user.restore_from_memento(user_data)

        game_data = game_state.get('game', {})
        self.game.day = game_data.get('day', 0)
        self.game.spend = game_data.get('spend', 0)
        self.game.clock = game_data.get('clock', datetime.datetime.now().hour)

        return True

    def _save_game(self) -> bool:
        if not self.current_user:
            return False

        game_state = {
            'user': self.current_user.create_memento(),
            'game': {
                'day': self.game.day,
                'spend': self.game.spend,
                'clock': self.game.clock
            }
        }
        return self.save_manager.save_game(self.current_user.username, game_state)

class Main:
    def __init__(self):
        self.facade = GameFacade()

    # === Authentication Menu ===
    def _auth_menu(self) -> int | None:
        print(Fore.CYAN + "─" * 39 + " " + "VIRTUAL PET GAME" + " " + "─" * 44)
        print(Fore.YELLOW + "1. Register")
        print(Fore.YELLOW + "2. Login")
        print(Fore.YELLOW + "3. Change Password")
        print(Fore.RED + "4. Exit")
        print(Fore.MAGENTA + GARIS)
        try:
            return int(input(Fore.GREEN + "Choose (1-4): ").strip())
        except ValueError:
            print(Fore.RED + "\nPlease insert digit at choice input!\n")
            return None

    def _register_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME).strip()
            password = input(
                "Password (Must contain at least 8 letters, 1 digit, and 2 symbols): "
            ).strip()

            if self.facade.register_user(username, password):
                break

            retry = input(
                "Would you like to register again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry != "Y":
                print("\n")
                break
            print("\n")

    def _login_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME).strip()
            password = input(INPUT_PASSWORD).strip()

            if self.facade.login_user(username, password):
                break

            print(GARIS)
            retry = input(
                "Would you like to login again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry != "Y":
                break

    def _logout_flow(self) -> None:
        if self.facade.current_user:
            print("\n💾 Saving your game...")
            self.facade.save_game()

        self.facade.logout_user()
        asyncio.run(loading())
        clear()

    def _change_password_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME).strip()
            password = input(INPUT_PASSWORD).strip()
            new_password = input("Your New Password: ").strip()

            if self.facade.change_password(username, password, new_password):
                print(Fore.GREEN + "\nPassword has been changed!\n" + Fore.RESET)
                input(Fore.YELLOW + "Press Enter to continue...")
                clear()
                break

            print(Fore.RED + "\nInvalid credentials or password!\n")
            print(GARIS)
            retry = input(
                "Would you like to change password again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry != "Y":
                break

    def _handle_auth_choice(self, choice: int) -> bool:
        actions = {
            1: self._register_flow,
            2: self._login_flow,
            3: self._change_password_flow,
            4: self._exit_game,
        }
        action = actions.get(choice)
        if action:
            action()
        else:
            print(Fore.RED + "Please type again...\n")
        return True

    def _auth_flow(self) -> None:
        while not self.facade.current_user:
            choice = self._auth_menu()
            if choice is None:
                continue
            print()
            self._handle_auth_choice(choice)

    # === Pet Zone Menu ===
    def _pet_zone_menu(self) -> int | None:
        print(Fore.CYAN + "─" * 43 + " " + "PET ZONE" + " " + "─" * 48)
        print(Fore.YELLOW + "1. Check time")
        print(Fore.YELLOW + "2. Show account info")
        print(Fore.YELLOW + "3. Create a new pet")
        print(Fore.YELLOW + "4. Interact with pet")
        print(Fore.YELLOW + "5. Pet stats")
        print(Fore.YELLOW + "6. Show Pets")
        print(Fore.YELLOW + "7. Go to shop")
        print(Fore.YELLOW + "8. Play Minigames")
        print(Fore.GREEN + "9. 💾 Save Game")
        print(Fore.RED + "10. Logout")
        print(Fore.MAGENTA + GARIS)
        try:
            return int(input(Fore.GREEN + "Choose (1-10): " + Fore.RESET).strip())
        except ValueError:
            print(Fore.RED + "\nPlease insert digit at choice input!\n")
            return None

    def _show_time_and_days(self) -> None:
        hours = self.facade.get_current_time()
        days = str(self.facade.get_current_day())
        print(Fore.RESET + self.facade.game.format.format_time_box(hours, days))

    def _show_account_info(self) -> bool:
        user = self.facade.current_user
        if not user:
            return False

        while True:
            stats = {
                "username": user.username,
                "pets": len(user.pets)
            }

            print("\n" + Fore.RESET + GARIS)
            print(Fore.YELLOW + "ACCOUNT INFORMATION".center(len(GARIS)) + Fore.RESET)
            print(GARIS)

            print(self.facade.game.format.format_username_box(
                stats["username"], user.pets))

            repeat = input("\nWould you like to view again? (Y/N): ").capitalize().strip()
            if repeat != "Y":
                print()
                break

        return True

    def _create_pet(self) -> bool:
        if not self.facade.current_user:
            print(Fore.YELLOW + "\nPlease login or register first.\n")
            return False

        if self.facade.create_pet():
            new_pet = self.facade.game.animal_list[-1]
            print(Fore.GREEN + f"\nYou adopted {new_pet.name} the {new_pet.type} {new_pet.emoji}!\n")
            return True

        print(Fore.RED + "Pet creation failed.\n")
        return False

    def _select_pet(self):
        pets = self.facade.get_pets()
        if not pets:
            print(Fore.RED + "\nYou have no pets yet. Create one first.\n")
            return None

        print(Fore.YELLOW + "\nYour pets:")
        for i, p in enumerate(pets, start=1):
            age = self.facade.get_pet_age(p)
            print(Fore.YELLOW + f"{i}. {p.name} ({p.type}) - Age: {age:.1f}")

        print(Fore.YELLOW + GARIS)

        try:
            idx = int(input(Fore.GREEN + "\nSelect pet number: ").strip())
        except ValueError:
            print(Fore.RED + "\nInvalid selection (Please input number).\n")
            return None

        if 1 <= idx <= len(pets):
            return pets[idx - 1]

        print(Fore.RED + "\nInvalid selection.\n")
        return None

    def _interact_with_pet(self) -> bool:
        pet = self._select_pet()
        if pet is None:
            return False

        if getattr(pet, "health", 1) > 0:
            self.facade.interact_pet(pet, self.facade.current_user)
            return True
        else:
            print(Fore.RED + "\nYour pet has deceased... 🧦\n")
            return False

    def _show_pet_stats(self) -> bool:
        pet = self._select_pet()
        if pet is None:
            return False

        self.facade.view_pet_stats(pet)

    async def _show_pet_stage(self) -> bool:
        pet = self._select_pet()
        if pet is None:
            return False

        if getattr(pet, "health", 1) > 0:
            stage = self.facade.get_pet_stage(pet)
            async for frame in stage:
                print(frame)
        else:
            print(Fore.RED + "\nYour pet has deceased... 🧦\n")
            return False

    def _go_to_shop(self) -> bool:
        self.facade.enter_shop()
        return True

    def _play_minigame_flow(self) -> bool:
        games = self.facade.get_minigames()
        if not games:
            print("\nNo minigames available.\n")
            return False

        print("\n" + GARIS)
        print("Minigames: ")
        print(GARIS)
        for i, name in enumerate(games, start=1):
            print(f"{i}. --> {name}")
        print(GARIS)

        try:
            idx = int(input("Choose a minigame number: ").strip())
        except Exception:
            print("Invalid choice.")
            return False

        if not (1 <= idx <= len(games)):
            print("Invalid choice.")
            return False

        if idx == 4 and len(User.users) < 2:
            print(Fore.RED + "\nNo other players available right now!")
            return True

        pet = self._select_pet()
        if pet is None:
            return True

        mg_name = games[idx - 1]
        self.facade.play_minigame(mg_name, pet)
        return True

    def _handle_pet_zone_choice(self, choice: int) -> bool:
        handlers = {
            1: lambda: self._show_time_and_days(),
            2: lambda: self._show_account_info(),
            3: lambda: self._create_pet(),
            4: lambda: self._interact_with_pet(),
            5: lambda: self._show_pet_stats(),
            6: lambda: asyncio.run(self._show_pet_stage()),
            7: lambda: self._go_to_shop(),
            8: lambda: self._play_minigame_flow(),
            9: lambda: self.facade.save_game(),
            10: lambda: self._logout_flow()
        }

        handler = handlers.get(choice)
        if handler:
            result = handler()
        else:
            print(Fore.RED + "\nPlease type again...\n")
            return True

        if result is not None:
            return bool(result)
        else:
            return result

    def _pet_zone_flow(self) -> None:
        asyncio.run(loading())
        clear()
        while self.facade.current_user:
            choice = self._pet_zone_menu()
            if choice is None:
                continue
            result = self._handle_pet_zone_choice(choice)
            if result is not None:
                if not result:
                    break
                else:
                    self.facade.spend_time()
                    asyncio.run(loading())
                    clear()

    def _exit_game(self) -> None:
        print(GARIS)
        sys.exit("Thank you for playing!".upper().center(len(GARIS)) + "\n")

    def run(self) -> None:
        print()
        while True:
            if not self.facade.current_user:
                self._auth_flow()
            else:
                self._pet_zone_flow()


if __name__ == "__main__":
    pet_game = Main()
    pet_game.run()

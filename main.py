from features.shop import Shop
from features.game import Game
from features.user import User, loading
import sys
from features.formatter import GARIS
from features.minigame import engine
import os
from typing import Dict, Any
import datetime
from features. save_manager import SaveManager
import asyncio
from colorama import Fore, init

init(autoreset=True)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

INPUT_USERNAME = "Username: "
INPUT_PASSWORD = "Password: "

class Main:
    def __init__(self):
        self.game = Game()           
        self.current_user = User.current_user
        self._minigame_engine = engine()
        self.save_manager = SaveManager.get_instance()  
        self._load_all_users_from_saves()
    
    def _load_all_users_from_saves(self):
        all_saves = self.save_manager._load_all_saves()
        
        for username, save_data in all_saves.items():
            if username not in User.users:
                user_data = save_data. get('user', {})
                password_hash = user_data.get('password', '')
                
                user = User(username, password_hash)
                
                user.restore_from_memento(user_data)
                
                User.users[username] = user
                
    def _get_current_game_state(self) -> Dict[str, Any]:
        """Get current game state for saving."""
        if not self.current_user:
            return {}
        
        user_data = self.current_user.create_memento()
        
        return {
            'user': user_data,
            'game': {
                'day': self.game.day,
                'spend': self.game.spend,
                'clock': self.game.clock
            }
        }
    
    def _save_game(self) -> bool:
        """Save current game state."""
        print(f"🔍 DEBUG: Attempting to save for user: {self.current_user.username if self.current_user else 'None'}")  # ← ADD THIS
        if not self.current_user:
            print(Fore.RED + "\nNo user logged in!\n")
            return False
        
        game_state = self._get_current_game_state()
        return self.save_manager.save_game(self.current_user. username, game_state)
    
    def _load_game(self, username: str) -> bool:
        """Load saved game state for user."""
        game_state = self. save_manager.load_game(username)
        
        if not game_state:
            return False
        
        # Restore user state
        user_data = game_state.get('user', {})
        self.current_user. restore_from_memento(user_data)
        
        # Restore game state
        game_data = game_state.get('game', {})
        self.game.day = game_data.get('day', 0)
        self.game.spend = game_data.get('spend', 0)
        self. game.clock = game_data. get('clock', datetime.datetime.now().hour)
        
        return True

    def _show_account_info(self, user: User) -> bool:
        while True:
            stats = {
                "username": user.username,
                "pets": len(user.pets)
            }

            print("\n" + Fore.RESET + GARIS)
            print(Fore.YELLOW + "ACCOUNT INFORMATION".center(len(GARIS)) + Fore.RESET)
            print(GARIS)

            print(self.game.format.format_username_box(
                    stats["username"], user.pets))

            repeat = input("\nWould you like to view again? (Y/N): ").capitalize().strip()
            if repeat != "Y":
                print()
                asyncio.run(loading())
                clear()
                self._pet_zone_flow()
                break  
            
        return True

    def create_pet(self) -> bool:
        if not self.current_user:
            print(Fore.YELLOW + "\nPlease login or register first.\n")
            return False

        flag = self.game.create()

        if self.game.animal_list and flag:
            new_pet = self.game.animal_list[-1]  
            self.current_user.add_pet(new_pet)
            print(Fore.GREEN + f"\nYou adopted {new_pet.name} the {new_pet.type} {new_pet.emoji}!\n")
            return True
        
        print(Fore.RED + "Pet creation failed.\n")
        return False

    def select_pet(self) -> bool | object:
        if not self.current_user:
            print(Fore.RED + "\nPlease login first.\n")
            return True

        pets = self.current_user.pets
        if not pets:
            print(Fore.RED + "\nYou have no pets yet. Create one first.\n")
            return True

        print(Fore.YELLOW + "\nYour pets:")
        for i, p in enumerate(pets, start=1):
            print(Fore.YELLOW + f"{i}. {p.name} ({p.type}) - Age: {p.get_age():.1f}")
        
        print(Fore.YELLOW + GARIS)

        try:
            idx = int(input(Fore.GREEN + "\nSelect pet number: ").strip())
        except ValueError:
            print(Fore.RED + "\nInvalid selection (Please input number).\n")
            return True

        if 1 <= idx <= len(pets):
            return pets[idx - 1]

        print(Fore.RED + "\nInvalid selection.\n")
        return True

    def show_pet_stats(self, pet: str) -> bool:
        self.game.view(pet)
        return True

    def interact_with_pet(self, pet: str, user: User) -> bool:
        self.game.interact(pet, user)
        return True

    def days(self) -> int:

        if (self.game.spend == 24):
            self.game.day += 1
        
        return self.game.day

    def time(self) -> str:
        clock = self.game.clock - 12 if self.game.clock > 12 else self.game.clock
        return f"{clock} A.M." if self.game.clock < 12 else f"{clock} P.M."
    
    def time_spend(self) -> None:
        self.game.spend += 1

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
            auth = User.register(username, password)

            if auth is not None:
                self.current_user = User.current_user
                break

            retry = input(
                "Would you like to register again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry == "Y":
                print("\n")
                clear()
                continue
            print("\n")
            break

    def _login_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME). strip()
            password = input(INPUT_PASSWORD).strip()
            auth = User.login(username, password)
            
            if auth is not None:
                self.current_user = User.current_user
                
                print("\n💾 Checking for saved game...")
                if self._load_game(username):
                    print(Fore.GREEN + "✅ Previous game loaded!\n")
                else:
                    print(Fore. YELLOW + "ℹ️ Starting fresh game.\n")
                
                break

            print(GARIS)
            retry = input(
                "Would you like to login again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry == "Y":
                continue
            break
    
    def _logout_flow(self) -> None:
        if self.current_user:
            print("\n💾 Saving your game...")
            self._save_game()
        
        User._logout()
        self.current_user = User.current_user
        asyncio.run(loading())
        clear()

    def _change_password_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME).strip()
            password = input(INPUT_PASSWORD).strip()
            new_password = input("Your New Password: ").strip()
            
            if not self._validate_user_credentials(username, password):
                print(GARIS)
                if not self._retry_prompt("change password"):
                    break
                continue
            
            user = User.users[username]
            if self._is_valid_new_password(new_password, password):
                user.password = new_password
                print(Fore.GREEN + "\nPassword has been changed!\n" + Fore.RESET)
                input(Fore.YELLOW + "Press Enter to continue...")
                clear()
                break
            
            print(GARIS)
            if not self._retry_prompt("change password"):
                break

    def _validate_user_credentials(self, username: str, password: str) -> bool:
        """Validate if username exists and password is correct."""
        if username not in User.users:
            print(Fore.RED + "\nPlease create your own username/password first!\n")
            return False
        
        user = User.users[username]
        if not User._check_password(password, user.password):
            print(Fore.RED + "\nWrong Previous Password!\n")
            return False
        
        return True

    def _is_valid_new_password(self, new_password: str, old_password: str) -> bool:
        """Check if new password is valid (not used before and different from old)."""
        users_password = [user_id.password for user_id in User.users.values()]
        
        if new_password in users_password or new_password == old_password:
            print(Fore.RED + "\nPassword has been used / same as previous password!\n")
            return False
        
        return True

    def _retry_prompt(self, action: str) -> bool:
        """Ask user if they want to retry an action."""
        retry = input(
            f"Would you like {action} again? (Y/N)\n"
            "(Note: input other than Y and N will be considered as N): "
        ).capitalize(). strip()
        clear()
        if retry == "Y":
            print("\n")
            asyncio.run(loading())
            clear()
            return True
        
        print("\n")
        return False

    def _play_minigame_flow(self) -> bool:
        games = self._minigame_engine.list_games()
        if not games:
            print("\nNo minigames available.\n")
            return False

        idx = self._get_minigame_choice(games)
        if idx is None:
            return False
        
        if idx == 4 and len(User.users) < 2:
            print(Fore. RED + "\nNo other players available right now!")
            return True

        mg_name = games[idx - 1]
        pet = self._select_pet_for_minigame()
        
        if pet is None:
            return True
        
        self._execute_minigame(mg_name, pet)
        return True

    def _get_minigame_choice(self, games: list) -> int | None:
        """Display minigame menu and get user's choice."""
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
            return None
        
        if not (1 <= idx <= len(games)):
            print("Invalid choice.")
            return None
        
        return idx

    def _select_pet_for_minigame(self) -> object | None:
        """Let user select a pet for the minigame."""
        if not self.current_user.pets:
            print(Fore. RED + "\nPlease create a pet first!")
            return None
        
        print(GARIS)
        print("\nYour pets:")
        for i, p in enumerate(self.current_user.pets, start=1):
            try:
                age = getattr(p, "get_age", lambda: 0)()
            except Exception:
                age = 0
            print(f"{i}. {p.name} ({getattr(p, 'type', 'pet')}) - Age: {age:.1f}")
        print(GARIS)
        
        try:
            choice = int(input("Choose pet number: ").strip())
        except Exception:
            print("Invalid!")
            return None
        
        if choice == 0 or not (1 <= choice <= len(self.current_user.pets)):
            print("Invalid pet selection!")
            return None
        
        return self.current_user.pets[choice - 1]

    def _execute_minigame(self, game_name: str, pet: object) -> None:
        """Execute the minigame and award rewards."""
        result = self._minigame_engine.play(game_name, self.current_user, pet)
        
        if not result:
            return
        
        coins = int(result. get("currency", 0))
        pet_happy = int(result.get("pet_happiness", 0))
        
        if coins:
            self._award_currency(coins)
        
        if pet and pet_happy:
            self._award_pet_happiness(pet, pet_happy)

    def _award_currency(self, coins: int) -> None:
        """Award currency to the current user."""
        self.current_user.currency += coins
        self.current_user.limit_currency()
        print(Fore.GREEN + f"\nYou received Rp. {'{:,}'.format(coins * 1000)}!\n")

    def _award_pet_happiness(self, pet: object, happiness: int) -> None:
        """Award happiness to the pet."""
        try:
            if hasattr(pet, "happiness"):
                happiness_increase = min(100, getattr(pet, "happiness", 0) + happiness)
                pet.happiness += happiness_increase
                print(Fore.GREEN + f"{pet.name}'s happiness has increased by {happiness_increase}.\n")
        except Exception:
            pass

    def _exit_game(self) -> None:
        if self.current_user:
            print("\n💾 Saving your game before exit...")
            self._save_game()
        
        print(GARIS)
        sys.exit("Thank you for playing!\n")

    def _invalid_auth_choice(self) -> None:
        print(Fore.RED + "Please type again...\n")

    def _handle_auth_choice(self, choice: int) -> bool:
        actions = {
            1: self._register_flow,
            2: self._login_flow,
            3: self._change_password_flow,
            4: self._exit_game,
        }
        actions.get(choice, self._invalid_auth_choice)()
        return True

    def _pet_zone_menu(self) -> int | None:
        print(Fore.CYAN + "─" * 43 + " " + "PET ZONE" + " " + "─" * 48)
        print(Fore. YELLOW + "1. Check time")
        print(Fore. YELLOW + "2. Show account info")
        print(Fore. YELLOW + "3. Create a new pet")
        print(Fore.YELLOW + "4. Interact with pet")
        print(Fore.YELLOW + "5. Pet stats")
        print(Fore. YELLOW + "6. Show Pets")
        print(Fore. YELLOW + "7. Go to shop")
        print(Fore. YELLOW + "8. Play Minigames")
        print(Fore. GREEN + "9. 💾 Save Game")  
        print(Fore. RED + "10. Logout")
        print(Fore. MAGENTA + GARIS)
        try:
            return int(input(Fore.GREEN + "Choose (1-10): " + Fore.RESET).strip())
        except ValueError:
            print(Fore.RED + "\nPlease insert digit at choice input!\n")
            return None


    def _show_time_and_days(self) -> None:
        hours = self.time()
        days = str(self.days())
        print(Fore.RESET + self.game.format.format_time_box(hours, days))

    def _interact_with_selected_pet(self) -> bool:
        pet = self.select_pet()
        if isinstance(pet, bool):
            return False
        if getattr(pet, "health", 1) > 0:
            self.interact_with_pet(pet, self.current_user)
            pet.time_past()
            return True
        else:
            print(Fore.RED + "\nYour pet has deceased... 🧦\n")
            return False

    def _show_selected_pet_stats(self) -> bool:
        pet = self.select_pet()
        if not isinstance(pet,bool):
            self.show_pet_stats(pet)
        else:
            return True

    async def _show_pet_stage(self) -> bool | None:
        pet = self.select_pet()
        if isinstance(pet,bool):
            return False
        if getattr(pet, "health", 1) > 0:
            age = pet.get_age()
            if age < 1:
                result = pet.baby() 
            elif 1 <= age < 3:
                result = pet.teen()
            elif 3 <= age < 10:
                result = pet.adult()
            else:
                result = pet.elder()

            async for frame in result:
                print(frame)

            return None
        else:
            print(Fore.RED + "\nYour pet has deceased... 🧦\n")
            return False

    def _go_to_shop(self) -> bool:
        shopping = Shop(self.current_user)
        shopping.interact()
        return True

    def _invalid_pet_zone_choice(self) -> bool:
        print(Fore.RED + "\nPlease type again...\n")
        return True

    def _handle_pet_zone_choice(self, choice: int) -> bool:
        handlers = {
            1: lambda: self._show_time_and_days(),
            2: lambda: self._show_account_info(self.current_user),
            3: lambda: self. create_pet(),
            4: lambda: self._interact_with_selected_pet(),
            5: lambda: self._show_selected_pet_stats(),
            6: lambda: asyncio.run(self._show_pet_stage()),
            7: lambda: self._go_to_shop(),
            8: lambda: self._play_minigame_flow(),
            9: lambda: self._save_game(),  
            10: lambda: self._logout_flow()  
        }
        handler = handlers.get(choice, lambda: self._invalid_pet_zone_choice())
        result = handler()
        self. time_spend()
        if (result):
            return bool(result)
        else:
            return result

    def _auth_flow(self) -> None:
        while not self.current_user:
            choice = self._auth_menu()
            if choice is None:
                continue
            print()
            self._handle_auth_choice(choice)

    def _pet_zone_flow(self) -> None:
        while self.current_user:
            choice = self._pet_zone_menu()
            if choice is None:
                continue
            result = self._handle_pet_zone_choice(choice)
            if result is not None:
                if not result:
                    break
                else:
                    asyncio.run(loading())
                    clear()

    def run(self) -> None:
        print()
        while True:
            if (not self.current_user):
                self._auth_flow()
            else:
                asyncio.run(loading())
                clear()
                self._pet_zone_flow()


if __name__ == "__main__":
    pet_game = Main()
    pet_game.run()
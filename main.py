from features.shop import Shop
from features.game import Game
from features.user import User, loading
import sys
from features.formatter import GARIS
import os
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

    def _show_account_info(self, user: User) -> bool:
        while True:
            stats = {
                "username": user.username,
                "password": user.password,
                "pets": len(user.pets)
            }

            print("\n" + Fore.RESET + GARIS)
            print(Fore.YELLOW + "ACCOUNT INFORMATION".center(len(GARIS)) + Fore.RESET)
            print(GARIS)

            show_password = input(
                "Would you like to show your password? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()

            if show_password == "Y":
                print(self.game.format.format_username_box(
                    stats["username"], stats["password"], user.pets, False))
            else:
                print(self.game.format.format_username_box(
                    stats["username"], stats["password"], user.pets, True))

            show_again = input(
                "\nWould you like to clear your account info? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()

            if show_again == "Y":
                print()
                asyncio.run(loading())
                clear()
                self._pet_zone_flow()
                break  

            repeat = input("\nWould you like to view again? (Y/N): ").capitalize().strip()
            if repeat != "Y":
                print("\n")
                break  
            
        return True


    def create_pet(self) -> bool:
        if not self.current_user:
            print(Fore.YELLOW + "\nPlease login or register first.\n")
            return True

        flag = self.game.create()

        if self.game.animal_list and flag:
            new_pet = self.game.animal_list[-1]  
            self.current_user.add_pet(new_pet)
            print(Fore.GREEN + f"\nYou adopted {new_pet.name} the {new_pet.type} {new_pet.emoji}!\n")
        else:
            print(Fore.RED + "Pet creation failed.\n")
        
        return True

    def select_pet(self) -> bool:
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
            if retry == "Y":
                print("\n")
                clear()
                continue
            print("\n")
            break

    def _login_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME).strip()
            password = input(INPUT_PASSWORD).strip()
            auth = User.login(username, password)
            
            if auth is not None:
                self.current_user = User.current_user
                break

            print(GARIS)
            retry = input(
                "Would you like to login again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            if retry == "Y":
                print("\n")
                asyncio.run(loading())
                clear()
                continue
            print("\n")
            break
    
    def _logout_flow(self) -> None:
        User._logout()
        self.current_user = User.current_user
        asyncio.run(loading())
        clear()

    def _change_password_flow(self) -> None:
        while True:
            username = input(INPUT_USERNAME).strip()
            password = input(INPUT_PASSWORD).strip()
            new_password = input("Your New Password: ").strip()
            
            if username in User.users:
                user = User.users[username]
                if password != user.password:
                    print(Fore.GREEN + "\nWrong Previous Password!\n")
                else:
                    users_password = [user_id.password for user_id in User.users.values()]
                    if new_password not in users_password and new_password != password:
                        user.password = new_password  
                        print(Fore.GREEN + "\nPassword has been changed!\n" + Fore.RESET)
                        input(Fore.YELLOW + "Press Enter to continue...")
                        clear()
                        break
                    else:
                        print(Fore.RED + "\nPassword has been used / same as previous password!\n")
            else:
                print(Fore.RED + "\nPlease create your own username/password first!\n")

            print(GARIS)
            retry = input(
                "Would you like change password again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            if retry == "Y":
                print("\n")
                asyncio.run(loading())
                clear()
                continue
            print("\n")
            break

    def _exit_game(self) -> None:
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
        print(Fore.YELLOW + "1. Check time")
        print(Fore.YELLOW + "2. Show account info")
        print(Fore.YELLOW + "3. Create a new pet")
        print(Fore.YELLOW + "4. Interact with pet")
        print(Fore.YELLOW + "5. Pet stats")
        print(Fore.YELLOW + "6. Show Pets")
        print(Fore.YELLOW + "7. Go to shop")
        print(Fore.RED + "8. Logout")
        print(Fore.MAGENTA + GARIS)
        try:
            return int(input(Fore.GREEN + "Choose (1-8): " + Fore.RESET).strip())
        except ValueError:
            print(Fore.RED + "\nPlease insert digit at choice input!\n")
            return None


    def _show_time_and_days(self) -> bool:
        hours = self.time()
        days = str(self.days())
        print(Fore.RESET + self.game.format.format_time_box(hours, days))
        return True

    def _interact_with_selected_pet(self) -> bool:
        pet = self.select_pet()
        if not pet:
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
        if pet:
            self.show_pet_stats(pet)
        return True
    

    async def _show_pet_stage(self) -> bool:
        pet = self.select_pet()
        if not pet:
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

            return True
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
            3: lambda: self.create_pet(),
            4: lambda: self._interact_with_selected_pet(),
            5: lambda: self._show_selected_pet_stats(),
            6: lambda: asyncio.run(self._show_pet_stage()),
            7: lambda: self._go_to_shop(),
            8: lambda: self._logout_flow(),
        }
        handler = handlers.get(choice, lambda: self._invalid_pet_zone_choice())
        result = handler()
        self.time_spend()
        asyncio.run(loading())
        clear()
        return bool(result)

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
            if not self._handle_pet_zone_choice(choice):
                break

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
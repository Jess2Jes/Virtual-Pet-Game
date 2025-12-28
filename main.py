import sys
import asyncio
from colorama import init
from constants.configs import LINE, USERNAME_INPUTTING, PASSWORD_INPUTTING
from features.user import User
from utils.gameFacade import GameFacade
from utils.colorize import (
    cyan, yellow, red, magenta, green, reset_color
)
from utils.formatter import clear
from utils.loading import loading_bar

import string

init(autoreset=True)



"""
main.py


Responsibilities:
- Provide a GameFacade that exposes coarse-grained operations used by the UI layer:
  registration/login, pet creation/interaction, shop and minigame access, and save/load.
- Provide the Main class that implements the console menus (authentication and pet zone)
  and wires user choices to GameFacade operations.
- Keep UI and business logic separated: Main handles I/O and formatting, GameFacade
  handles application state and coordination.

Notes:
- This file is console-driven and uses asyncio.run(...) in a few places when showing
  the loading progress bar from features.user.loading.
- No game rules or persistent logic were changed — only docstrings and comments were added
  to make the code easier to navigate and maintain.
"""



class Main:
    """
    Console-driven main application that displays menus and delegates actions to GameFacade.

    Main keeps the user-facing input/output loops and uses asyncio.run where appropriate
    to show a small loading progress bar.
    """

    def __init__(self):
        self.facade = GameFacade()

    def _auth_menu(self) -> int | None:
        """Render the authentication menu and collect a numeric choice from the user."""
        print(cyan("─" * 51 + " " + "VIRTUAL PET GAME" + " " + "─" * 51))
        print(yellow("1. Register"))
        print(yellow("2. Login"))
        print(yellow("3. Change Password"))
        print(red("4. Exit"))
        print(magenta(LINE))
        try:
            return int(input(green("Choose (1-4): ")).strip())
        except ValueError:
            print(red("\nPlease insert digit at choice input!\n"))
            return None

    def _register_flow(self) -> None:
        """Interactive registration flow: ask for username/password and attempt registration."""
        while True:
            username = input(USERNAME_INPUTTING).strip()
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
        """Interactive login flow: prompt for credentials and attempt login."""
        while True:
            username = input(USERNAME_INPUTTING).strip()
            password = input(PASSWORD_INPUTTING).strip()

            if self.facade.login_user(username, password):
                break

            print(LINE)
            retry = input(
                "Would you like to login again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry != "Y":
                break

    def _logout_flow(self) -> None:
        """Save the current user's game and perform logout."""
        if self.facade.current_user:
            print("\n💾 Saving your game...")
            self.facade.save_game()

        self.facade.logout_user()
        asyncio.run(loading_bar())
        clear()

    def _change_password_flow(self) -> None:
        """Prompt for credentials and new password, then attempt to change it."""
        while True:
            username = input(USERNAME_INPUTTING).strip()
            password = input(PASSWORD_INPUTTING).strip()
            new_password = input("Your New Password: ").strip()

            if self.facade.change_password(username, password, new_password):
                print(green("\nPassword has been changed!\n"))
                input(yellow("Press Enter to continue..."))
                clear()
                break

            print(red("\nInvalid credentials or password!\n"))
            print(LINE)
            retry = input(
                "Would you like to change password again? (Y/N)\n"
                "(Note: input other than Y and N will be considered as N): "
            ).capitalize().strip()
            clear()
            if retry != "Y":
                break

    def _handle_auth_choice(self, choice: int) -> bool:
        """Dispatch an authentication menu choice to the appropriate flow."""
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
            print(red("Please type again...\n"))
        return True

    def _auth_flow(self) -> None:
        """Loop until a user is authenticated (register/login/change-password/exit)."""
        while not self.facade.current_user:
            choice = self._auth_menu()
            if choice is None:
                continue
            print()
            self._handle_auth_choice(choice)

    def _pet_zone_menu(self) -> int | None:
        """Render the main pet-zone menu and collect the user's choice."""
        print(cyan("─" * 55 + " " + "PET ZONE" + " " + "─" * 55))
        print(yellow("1. Check time"))
        print(yellow("2. Show account info"))
        print(yellow("3. Create a new pet"))
        print(yellow("4. Interact with pet"))
        print(yellow("5. Pet stats"))
        print(yellow("6. Show Pets"))
        print(yellow("7. Go to shop"))
        print(yellow("8. Play Minigames"))
        print(green("9. 💾 Save Game"))
        print(red("10. Logout"))
        print(magenta(LINE))
        try:
            return int(input(green("Choose (1-10): ")).strip())
        except ValueError:
            print(red("\nPlease insert digit at choice input!\n"))
            return None

    def _show_time_and_days(self) -> None:
        """Display the game's current time and day using the formatter box."""
        hours = self.facade.get_current_time()
        days = str(self.facade.get_current_day())
        print(reset_color(self.facade.game.format.format_time_box(hours, days)))

    def _show_account_info(self) -> bool:
        """Show a short account information panel with username and number of pets."""
        user = self.facade.current_user
        if not user:
            return False

        while True:
            stats = {
                "username": user.username,
                "pets": len(user.pets),
            }

            print((f'\n{reset_color(LINE)}'))
            print(yellow("ACCOUNT INFORMATION".center(len(LINE))))
            print(reset_color(LINE))

            print(self.facade.game.format.format_username_box(stats["username"], user.pets))

            repeat = input("\nWould you like to view again? (Y/N): ").capitalize().strip()
            if repeat != "Y":
                print()
                break

        return True

    def _create_pet(self) -> bool:
        """Create and adopt a new pet for the current user."""
        if not self.facade.current_user:
            print(yellow("\nPlease login or register first.\n"))
            return False

        if self.facade.create_pet():
            new_pet = self.facade.game.animal_list[-1]
            print(green(f"\nYou adopted {new_pet.name} the {new_pet.type} {new_pet.emoji}!\n"))
            return True

        print(red("Pet creation failed.\n"))
        return False

    def _select_pet(self):
        """Present the user's pets and return the selected pet instance or None."""
        pets = self.facade.get_pets()
        if not pets:
            print(red("\nYou have no pets yet. Create one first.\n"))
            return None

        print(yellow("\nYour pets:"))
        for i, p in enumerate(pets, start=1):
            age = self.facade.get_pet_age(p)
            print(yellow(f"{i}. {p.name} ({p.type}) - Age: {age:.1f}"))

        print(yellow(LINE))

        try:
            idx = int(input(green("\nSelect pet number: ")).strip())
        except ValueError:
            print(red("\nInvalid selection (Please input number).\n"))
            return None

        if 1 <= idx <= len(pets):
            return pets[idx - 1]

        print(red("\nInvalid selection.\n"))
        return None

    def _interact_with_pet(self) -> bool:
        """Begin an interaction session with a selected pet if it is alive."""
        pet = self._select_pet()
        if pet is None:
            return False

        if getattr(pet, "health", 1) > 0:
            self.facade.interact_pet(pet)
            return True
        else:
            print(red("\nYour pet has deceased... 🧦\n"))
            return False

    def _show_pet_stats(self) -> bool:
        """Select a pet and display its full status box."""
        pet = self._select_pet()
        if pet is None:
            return False

        self.facade.view_pet_stats(pet)
        return True

    async def _show_pet_stage(self) -> bool:
        """
        Show an animated/staged representation of the pet's life stage.

        The pet stage methods (baby/teen/adult/elder) are expected to be iterable
        or asynchronous iterables that yield frames to print.
        """
        pet = self._select_pet()
        if pet is None:
            return False

        if getattr(pet, "health", 1) > 0:
            stage = self.facade.get_pet_stage(pet)
            for frame in stage:
                print(frame)
            return True
        else:
            print(red("\nYour pet has deceased... 🧦\n"))
            return False

    def _go_to_shop(self) -> bool:
        """Open the shop UI for the current user."""
        self.facade.enter_shop()
        return True

    def _play_minigame_flow(self) -> bool:
        """Interactive flow to choose and play a minigame with a selected pet."""
        games = self.facade.get_minigames()
        if not games:
            print("\nNo minigames available.\n")
            return False

        print("\n" + LINE)
        print("Minigames: ")
        print(LINE)
        for i, name in enumerate(games, start=1):
            print(f"{i}. --> {name}")
        print(LINE)

        idx = input("Choose a minigame number (or type 'q' to quit): ").strip().lower()
        
        if idx == 'q':
            print(green("\nExit from minigame!"))
            return True

        if not (1 <= int(idx) <= len(games)) and idx != 'q':
            print("Invalid choice.")
            return False

        if int(idx) == 4 and len(User.users) < 2:
            print(red("\nNo other players available right now!"))
            return True

        pet = self._select_pet()
        if pet is None:
            return True

        mg_name = games[int(idx) - 1]
        self.facade.play_minigame(mg_name, pet)
        return True

    def _handle_pet_zone_choice(self, choice: int) -> bool:
        """Dispatch pet-zone menu choices to handler methods and manage results."""
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
            10: lambda: self._logout_flow(),
        }

        handler = handlers.get(choice)
        if handler:
            result = handler()
        else:
            print(red("\nPlease type again...\n"))
            return True

        if result is not None:
            return bool(result)
        else:
            return result

    def _pet_zone_flow(self) -> None:
        """Main loop for the pet zone where the player performs actions with pets or shop/minigames."""
        asyncio.run(loading_bar())
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
                    asyncio.run(loading_bar())
                    clear()

    def _exit_game(self) -> None:
        """Exit the application politely."""
        print(LINE)
        sys.exit("Thank you for playing!".upper().center(len(LINE)) + "\n")

    def run(self) -> None:
        """Run the main application loop: authenticate then enter pet zone."""
        print()
        while True:
            if not self.facade.current_user:
                self._auth_flow()
            else:
                self._pet_zone_flow()


if __name__ == "__main__":
    pet_game = Main()
    pet_game.run()
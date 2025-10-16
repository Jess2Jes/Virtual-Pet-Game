from features.shop import Shop
from features.game import Game
from features.user import User
import sys
from features.formatter import GARIS
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

INPUT_USERNAME = "Username: "
INPUT_PASSWORD = "Password: "

class Main:
    def __init__(self):
        self.game = Game()           
        self.current_user = None

    def create_pet(self) -> None:
        if not self.current_user:
            print("\nPlease login or register first.\n")
            return

        self.game.create()

        if Game.animal_list:
            new_pet = Game.animal_list[-1]  
            self.current_user.add_pet(new_pet)
            print(f"\nYou adopted {new_pet.name} the {new_pet.type}!\n")
        else:
            print("Pet creation failed.")

    def select_pet(self) -> None:
        if not self.current_user:
            print("\nPlease login first.\n")
            return None

        pets = self.current_user.pets
        if not pets:
            print("\nYou have no pets yet. Create one first.\n")
            return None

        print("\nYour pets:")
        for i, p in enumerate(pets, start=1):
            print(f"{i}. {p.name} ({p.type}) - Age: {p.get_age():.1f}")

        try:
            idx = int(input("\nSelect pet number: ").strip())
        except ValueError:
            print("\nInvalid selection.\n")
            return None

        if 1 <= idx <= len(pets):
            return pets[idx - 1]

        print("\nInvalid selection.\n")
        return None

    def show_pet_stats(self, pet) -> None:
        self.game.view(pet)

    def interact_with_pet(self, pet) -> None:
        self.game.interact(pet)

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
        print("─" * 39 + " " + "VIRTUAL PET GAME" + " " + "─" * 44)
        print("1. Register")
        print("2. Login")
        print("3. Change Password")
        print("4. Exit")
        print(GARIS)
        try:
            return int(input("Choose (1-4): ").strip())
        except ValueError:
            print("\nPlease insert digit at choice input!\n")
            return None

    def _handle_auth_choice(self, choice: int) -> bool:
        if choice == 1:
            while True:
                username = input(INPUT_USERNAME).strip()
                password = input(
                    "Password (Must contain at least 8 letters, 1 digit, and 2 symbols): "
                ).strip()
                auth = User.register(username, password)

                if auth is not None:
                    self.current_user = User.current_user
                    break
                else:
                    register_chances = input("Would you like to register again? (Y/N)\n" \
                    "(Note: input other than Y and N will be considered as N): ").capitalize().strip()
                    if (register_chances == "Y"):
                        print("\n")
                        clear()
                    else:
                        print("\n")
                        break

        elif choice == 2:
            while True:
                username = input(INPUT_USERNAME).strip()
                password = input(INPUT_PASSWORD).strip()
                auth = User.login(username, password)
                
                if auth is not None:
                    self.current_user = User.current_user
                    break
                else:
                    print(GARIS)
                    login_chances = input("Would you like to login again? (Y/N)\n" \
                        "(Note: input other than Y and N will be considered as N): ").capitalize().strip()
                    if (login_chances == "Y"):
                        print("\n")
                        clear()
                    else:
                        print("\n")
                        break

        elif choice == 3:
            while True:
                username = input(INPUT_USERNAME).strip()
                password = input(INPUT_PASSWORD).strip()
                new_password = input("Your New Password: ").strip()
                
                if (username in User.users):
                    user = User.users[username]
                    if (password != user.password):
                        print("\nPassword sebelumnya salah!\n")
                    else:
                        user.password = new_password
                        if (user.password != password):
                            print("\nPassword berhasil diubah!\n")
                            input("Tekan Enter untuk melanjutkan...")
                            clear()
                            break
                else:
                    print("\nPlease create your own username/password first!")

                print("\n" + GARIS)
                change_chances = input("Would you like change password again? (Y/N)\n" \
                    "(Note: input other than Y and N will be considered as N): ").capitalize().strip()
                if (change_chances == "Y"):
                    print("\n")
                    clear()
                else:
                    print("\n")
                    break
            
        elif choice == 4:
            print(GARIS)
            sys.exit("Thank you for playing!\n")
        else:
            print("Please type again...\n")
        return True

    def _pet_zone_menu(self) -> int | None:
        print("─" * 43 + " " + "PET ZONE" + " " + "─" * 48)
        print("1. Check time")
        print("2. Create a new pet")
        print("3. Interact with pet")
        print("4. Pet stats")
        print("5. Show Pets")
        print("6. Go to shop")
        print("7. Logout")
        print(GARIS)
        try:
            return int(input("Choose (1-7): ").strip())
        except ValueError:
            print("\nPlease insert digit at choice input!\n")
            return None

    def _show_time_and_days(self) -> bool:
        print("\n" + GARIS)
        print("Time".center(101))
        print(GARIS)
        print(f"Time: {self.time()}")
        print(GARIS)
        print("\n" + GARIS)
        print("Day Spent Playing Virtual Pet Game".center(101))
        print(GARIS)
        print(f"Days: {self.days()} days")
        print(GARIS + "\n")
        return True

    def _interact_with_selected_pet(self) -> bool:
        pet = self.select_pet()
        if not pet:
            # No pet selected; report unsuccessful interaction
            return False
        if getattr(pet, "health", 1) > 0:
            self.interact_with_pet(pet)
            pet.time_past()
            return True
        else:
            print("\nYour pet has deceased... 🧦\n")
            return False

    def _show_selected_pet_stats(self) -> bool:
        pet = self.select_pet()
        if pet:
            self.show_pet_stats(pet)
        return True

    def _show_pet_stage(self) -> bool:
        pet = self.select_pet()
        if not pet:
            # No pet selected; report unsuccessful stage display
            return False
        if getattr(pet, "health", 1) > 0:
            age = pet.get_age()
            if age < 1:
                pet.baby()
            elif 1 <= age < 3:
                pet.teen()
            elif 3 <= age < 10:
                pet.adult()
            else:
                pet.elder()
            return True
        else:
            print("\nYour pet has deceased... 🧦\n")
            return False

    def _go_to_shop(self) -> bool:
        shopping = Shop(User.current_user)
        shopping.interact()
        return True

    def _logout(self) -> bool:
        User.current_user = None
        self.current_user = None
        print()
        return False

    def _invalid_pet_zone_choice(self) -> bool:
        print("\nPlease type again...\n")
        return True

    def _handle_pet_zone_choice(self, choice: int) -> bool:
        handlers = {
            1: self._show_time_and_days,
            2: self.create_pet,
            3: self._interact_with_selected_pet,
            4: self._show_selected_pet_stats,
            5: self._show_pet_stage,
            6: self._go_to_shop,
            7: self._logout,
        }
        handler = handlers.get(choice, self._invalid_pet_zone_choice)

        if handler is self._logout:
            result = handler()
        else:
            handler()
            result = True  

        self.time_spend()
        return bool(result)

    def _auth_flow(self) -> None:
        while not User.current_user:
            choice = self._auth_menu()
            if choice is None:
                continue
            print()
            self._handle_auth_choice(choice)

    def _pet_zone_flow(self) -> None:
        while User.current_user:
            choice = self._pet_zone_menu()
            if choice is None:
                continue
            if not self._handle_pet_zone_choice(choice):
                break

    def run(self) -> None:
        print()
        while True:
            if not User.current_user:
                self._auth_flow()
            else:
                self._pet_zone_flow()


if __name__ == "__main__":
    pet_game = Main()
    pet_game.run()
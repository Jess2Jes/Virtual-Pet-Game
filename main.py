from features.shop import Shop
from features.game import Game
from features.user import User


import sys

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
            new_pet = Game.animal_list[-1]  # last created pet
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
        clock = 0
        if (self.game.clock > 12):
            clock = self.game.clock - 12
        else:
            clock = self.game.clock
        
        if (self.game.clock < 12):
            return f"{clock} A.M."
        else:
            return f"{clock} P.M."
    
    def time_spend(self) -> None:
        self.game.spend += 1

    def run(self) -> None:

        print()

        while True:
            if not User.current_user:
                print("─" * 39 + " " + "VIRTUAL PET GAME" + " " + "─" * 44)
                print("1. Register")
                print("2. Login")
                print("3. Change Password")
                print("4. Exit")
                print("─" * 101)

                try:
                    choice = int(input("Choose (1-4): ").strip())
                except ValueError:
                    print("\nPlease insert digit at choice input!\n")
                    continue

                print()
                if choice == 1:
                    username = input("Username: ").strip()
                    password = input(
                        "Password (Must contain at least 8 letters, 1 digit, and 2 symbols): "
                    ).strip()
                    User.register(username, password)
                    self.current_user = User.current_user

                elif choice == 2:
                    username = input("Username: ").strip()
                    password = input("Password: ").strip()
                    User.login(username, password)
                    self.current_user = User.current_user
                
                elif choice == 3:
                    username = input("Username: ").strip()
                    password = input("Password: ").strip()
                    new_password = input("Your New Password: ").strip()
                    if (username in User.users):
                        user = User.users[username]
                        if (password != user.password):
                            print("\nWrong Previous Password! Change Password Operation Unsuccessful!")
                        else:
                            user.password = new_password
                    else:
                        print("\nPlease create your own username/password first!")
                    
                    print("\n")
                    
                elif choice == 4:
                    print("─" * 101)
                    sys.exit("Thank you for playing!\n")
                else:
                    print("Please type again...\n")

            else:
                while True:
                    print("─" * 43 + " " + "PET ZONE" + " " + "─" * 48)
                    print("1. Check time")
                    print("2. Create a new pet")
                    print("3. Interact with pet")
                    print("4. Pet stats")
                    print("5. Show Pets")
                    print("6. Go to shop")
                    print("7. Logout")
                    print("─" * 101)

                    try:
                        choice = int(input("Choose (1-7): ").strip())
                    except ValueError:
                        print("\nPlease insert digit at choice input!\n")
                        continue

                    if choice == 1:
                        print("\n" + "─"*101)
                        print("Time".center(101))
                        print("─"*101)
                        print(f"Time: {self.time()}")
                        print("─"*101)
                        print("\n" + "─"*101)
                        print("Day Spent Playing Virtual Pet Game".center(101))
                        print("─"*101)
                        print(f"Days: {self.days()} days")
                        print("─"*101 + "\n")

                    elif choice == 2:
                        self.create_pet()

                    elif choice == 3:
                        pet = self.select_pet()
                        if pet:
                            if getattr(pet, "health", 1) > 0:
                                self.interact_with_pet(pet)
                                pet.time_past()
                            else:
                                print("\nYour pet has deceased... 🪦\n")

                    elif choice == 4:
                        pet = self.select_pet() 
                        if pet: 
                            self.show_pet_stats(pet)

                    elif choice == 5:
                        pet = self.select_pet()
                        if pet:
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
                            else:
                                print("\nYour pet has deceased... 🪦\n")
                        
                        
                    elif choice == 6:
                        shopping = Shop(User.current_user)
                        shopping.interact()

                    elif choice == 7:
                        User.current_user = None
                        self.current_user = None
                        print()
                        break

                    else:
                        print("\nPlease type again...\n")
                    
                    self.time_spend()


if __name__ == "__main__":
    pet_game = Main()
    pet_game.run()

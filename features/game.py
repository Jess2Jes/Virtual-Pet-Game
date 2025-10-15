import datetime
from random import randrange, choice as ch
from .animal import Cat, Rabbit, Dino, Dragon, Pou, VirtualPet
from .formatter import Formatter, GARIS
from .user import User

class Game:
    animal_list = []

    def __init__(self):
        self.clock = datetime.datetime.now().hour
        self.format = Formatter()
        self.spend = 0
        self.day = 0
    
    @staticmethod
    def get_currency() -> int:
        return User.current_user.currency
    
    @classmethod
    def create(cls) -> None:
        print()
        print("─"*36 + " " + "Create Your Own Pet" + " " + "─"*44)
        name = input("Name your pet: ").title().strip()
        print(GARIS)
        print("Here's five types of species you can choose: ")
        print("1. Cat")
        print("2. Rabbit")
        print("3. Dinosaur")
        print("4. Dragon")
        print("5. Pou")
        print(GARIS)
        
        species_map = {
            "cat": Cat,
            "rabbit": Rabbit,
            "dinosaur": Dino,
            "dragon": Dragon,
            "pou": Pou,
        }

        while True: 
            species = input("Choose his/her species (input type of species here): ").lower().strip()
            cls_type = species_map.get(species)
            if cls_type:
                animal = cls_type(name, 0)
                cls.animal_list.append(animal)
                break
            print("Choose the correct species!")
            print()

        print()
        print(GARIS)
        print(f"{name}, a {species}, has born!")
        print(GARIS)
    
    
    def view(self, pet) -> None:
        stats = {
            "name": pet.name,
            "type": pet.type,
            "age": f"{pet.get_age():.1f}",
            "hunger": pet.hunger,
            "fat": pet.fat,
            "sanity": pet.sanity,
            "happiness": pet.happiness,
            "energy": pet.energy,
            "health": pet.health,
            "mood": pet.get_mood(),
            "summary": pet.get_summary(),
            "age_summary": pet.get_age_summary()
        }
        print(self.format.format_status_box(stats))

    @staticmethod
    def get_health(pet) -> int:
        return pet.health
    
    @staticmethod
    def _print_main_interact_menu() -> None:
        print("\n" + "="*101)
        print("1. Feed")
        print("2. Play")
        print("3. Bath")
        print("4. Give Potion")
        print("5. Sleep")
        print("6. Take a walk")
        print("7. Talk to pet")
        print("8. Exit")
        print(GARIS)

    @staticmethod
    def _input_int(prompt: str):
        try:
            return int(input(prompt))
        except ValueError:
            return None

    @staticmethod
    def _print_stock(title: str, store: dict) -> None:
        print("\n" + GARIS)
        print(title)
        print(GARIS + "\n")
        for key in store.keys():
            vals = store[key]
            if len(vals) == 3:
                print(f"- {key} (Hunger: {vals[1]}, Happiness: {vals[2]}, Available: {vals[0]})")
            elif len(vals) == 2:
                print(f"- {key} (Available: {vals[0]})")
            else:
                print(f"- {key} (Available: {vals[0]})")
    
    @staticmethod
    def _print_potion_requirement(title: str) -> None:
        print("\n" + GARIS)
        print(title)
        print(GARIS)
        print("1. Fat Burner can be used if your energy is below 50.")
        print("2. Health Potion can be used if your health is below 100.")
        print("3. Energizer can be used if your energy is below 100.")
        print("4. Adult Potion can be used if your age is below 20.")
        print(GARIS + "\n")

    @staticmethod
    def _feed(pet: VirtualPet) -> None:
        food = input("\nWhich food (input food's name)? ").title().strip()
        pet.feed(food)

    @staticmethod
    def _play(pet: VirtualPet) -> None:
        
        if pet.energy < 10:
            print(f"\n{pet.name} is too tired to play..")
            return
        if pet.hunger < 30:
            print(f"\n{pet.name} is too hungry to play..")
            return
        if pet.health < 20:
            print(f"\n{pet.name} is too sick to play..")
            return

        act = {
            "cat": "You play laser with",
            "rabbit": "You play catch ball with",
            "dinosaur": "You play hide and seek with",
            "dragon": "You play fireball with",
            "pou": "You brought to swimming pool"

        }.get(pet.type.lower(), "You play with")

        emoji = {
            "cat": "💥", "rabbit": "🤾", "dinosaur": "🏃",
            "dragon": "☄️", "pou": "🏊‍♂️"

        }.get(pet.type.lower(), "🎲")

        print(f"\n{act} {pet.name} {emoji}!")

        print(f"\n{pet.name}'s happiness increased by 10.")
        print(f"{pet.name}'s hunger decreased by 5.")
        print(f"{pet.name}'s energy decreased by 5.")
        print("You earned Rp. 25,000!")

        pet.happiness += 10
        pet.hunger -= 5
        pet.energy -= 5
        User.current_user.currency += 25000

        pet.limit_stat()

        print("\n" + "="*101)
        print(f"Happiness : {pet.happiness}")
        print(f"Hunger: {pet.hunger}")
        print(f"Energy: {pet.energy}")
        print(GARIS)

    @staticmethod
    def _bath(pet: VirtualPet) -> None:
        soap = input("\nWhich soap (input soap's name)? ").title().strip()
        pet.bath(soap)

    @staticmethod
    def _give_potion(pet: VirtualPet) -> None:
        potion = input("\nWhich potion (input potion's name)? ").title().strip()
        pet.health_care(potion)

    def _sleep(self, pet: VirtualPet) -> None:

        hours = self._input_int(f"\n{pet.name}'s sleep duration (1-12): ")

        if hours is None:
            print("\nPlease insert digit at choice input!\n")
            return
        
        if not (1 <= hours <= 12):
            print("\nSleep duration must between 1 to 12 hours.")
            return
        
        pet.sleep(hours)

    @staticmethod
    def _walk(pet: VirtualPet) -> None:
        if pet.energy < 10:
            print(f"\n{pet.name} is too tired to take a walk..")
            return
        if pet.hunger < 30:
            print(f"\n{pet.name} is too hungry to take a walk..")
            return
        if pet.health < 20:
            print(f"\n{pet.name} is too sick to take a walk..")
            return

        random_event = randrange(0, 50)
        print(f"\nYou take {pet.name} for a walk!")

        if random_event == 10:
            print("\nYou found a wallet in your way home!")
            print("You brought back home Rp. 25,000...")
            User.current_user.currency += 25000
        elif random_event == 30:
            print("\nYour pet stepped on mud!")
            print(f"{pet.name}' sanity decreased (-10)...")
            pet.sanity -= 10
        elif random_event == 20:
            print("\nYour pet ate rotten apple!")
            print(f"{pet.name}'s health decreased (-15)...")
            pet.health -= 15
        elif random_event == 4:
            print("\nYour pet got run over by car!")
            print(f"{pet.name} deceased... 💀\n")
            pet.health -= 100
            pet.limit_stat()
            return
        elif random_event == 50:
            print("\nYou got robbed on your way home!")
            print("You lose Rp. 100,000!")
            User.current_user.currency -= 100000
            User.limit_currency()

        pet.happiness += 25
        pet.hunger -= 5
        pet.energy -= 15
        
        print(f"{pet.name}'s hunger decreased by 5.")
        print(f"{pet.name}'s energy decreased by 15.")

        pet.limit_stat()

        print("\n" + "="*101)
        print(f"Happiness : {pet.happiness}")
        print(f"Hunger: {pet.hunger}")
        print(f"Energy: {pet.energy}")
        print(GARIS)
    
    def _talk_menu(self, pet: VirtualPet) -> None:
        while True:
            print(GARIS)
            print("Topic of Conversation: ")
            print(GARIS)
            print("1. What do you want to do today?")
            print("2. What is your favourite food?")
            print("3. Can you give me money?")
            print("4. Tell a joke")
            print("5. Goodbye")
            print(GARIS)
            topic = self._input_int("Choose a topic: ")

            if topic is None:
                print("\nPlease type a number.")
                continue

            if topic == 1:
                ans = [
                    f"I want to eat {pet.fav_food}!", "I want to play :D", 
                    "I want to take a walk 🌳.","I want to take a bath :)",
                    "I want to talk to you..👉👈"
                ]
                print(f"\n{pet.name}: {ch(ans)}")

            elif topic == 2:
                print(f"\n{pet.name}: My favourite food is {pet.fav_food}. :D")
            
            elif topic == 3:
                if all(val < 50 for val in [pet.hunger, pet.sanity, pet.happiness, pet.health]):
                    print(f"\n{pet.name}: I will consider it if you take care of me properly!")
                else:
                    if pet.generosity < 2:
                        print(f"\n{pet.name}: Here, I'll give you Rp. 100,000.")
                        User.current_user.currency += 100000
                        pet.generosity += 1
                    else:
                        print(f"\n{pet.name}: Sorry, can't give you anymore... 😔")
            
            elif topic == 4:
                jokes = [
                    "Why can't a nose be 12 inches long? Because then it would be a foot!",
                    "How much do rainbows weigh? Not much. They're actually pretty light!",
                    "I had a joke about paper today, but it was tearable!",
                    "What do you call an ant who fights crime? A vigilANTe!",
                    "How do you make holy water? You boil the hell out of it!",
                    "Some people pick their nose, but I was born with mine.",
                    "Justice is a dish best served cold. Otherwise, it's just water.",
                    "Why don't programmers like nature? Too many \"bugs\".",
                    "Why don't robots panic? \"Nerves of steel\"."
                ]

                if pet.hunger < 30:
                    print(f"\n{pet.name} is too hungry to joke right now..")

                elif pet.health < 20:
                    print(f"\n{pet.name} is too sick to joke right now..")

                elif pet.energy < 10:
                    print(f"\n{pet.name} is too tired to joke right now..")

                elif pet.happiness < 20:
                    print(f"\n{pet.name} is too stressed to joke right now..")

                else:
                    print(f"\n{pet.name}: {ch(jokes)} Haha 🤭, funny right?")
            
            elif topic == 5:
                print(f"\n{pet.name}: Okay, goodbye!")
                print(f"{pet.name}'s happiness has increased by 10.")
                pet.happiness += 10
                break

            print()

    def _stocks(self) -> dict:
        return {
            1: ["List of Foods:", VirtualPet.list_food],
            3: ["List of Soaps:", VirtualPet.list_soap],
            4: ["List of Potions:", VirtualPet.list_potion],
        }

    def _actions(self):
        return {
            1: lambda p: self._feed(p),
            2: lambda p: self._play(p),
            3: lambda p: self._bath(p),
            4: self._action_potion,
            5: lambda p: self._sleep(p),
            6: lambda p: self._walk(p),
            7: lambda p: self._talk_menu(p),
        }

    def _action_potion(self, pet: VirtualPet) -> None:
        self._print_potion_requirement("Potion Usage Requirement")
        self._give_potion(pet)

    @staticmethod
    def _is_valid_choice(choice: int) -> bool:
        return 1 <= choice <= 8

    def _should_show_stock(self, choice: int) -> bool:
        return choice in self._stocks()

    def interact(self, pet) -> None:
        print("\n" + "="*101)
        print(f"Playing with {pet.name}, the {pet.type}:")
        while True:
            self._print_main_interact_menu()
            choice = self._input_int("Choose (1-8): ")

            if choice is None:
                print("\nPlease enter digit!")
                continue

            if choice == 8:
                print()
                break

            if not self._is_valid_choice(choice):
                print("\nPlease choose from (1-8).")
                continue

            if self._should_show_stock(choice):
                title, store = self._stocks()[choice]
                self._print_stock(title, store)

            action = self._actions().get(choice)
            if action:
                action(pet)

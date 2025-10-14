import datetime
from random import randrange, choice as ch
from .animal import Cat, Rabbit, Dino, Dragon, Pou, VirtualPet
from .formatter import Formatter
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
        name = input("Name your pet: ").title()
        print("─"*101)
        print("Here's five types of species you can choose: ")
        print("1. Cat")
        print("2. Rabbit")
        print("3. Dinosaur")
        print("4. Dragon")
        print("5. Pou")
        print("─"*101)
        
        while True: 
            species = input("Choose his/her species (input type of species here): ").lower()

            if species == "cat":
                animal = Cat(name, 0)
                cls.animal_list.append(animal)
                break
            elif species == "rabbit":
                animal = Rabbit(name, 0)
                cls.animal_list.append(animal)
                break
            elif species == "dinosaur":
                animal = Dino(name, 0)
                cls.animal_list.append(animal)
                break
            elif species == "dragon":
                animal = Dragon(name, 0)
                cls.animal_list.append(animal)
                break
            elif species == "pou":
                animal = Pou(name, 0)
                cls.animal_list.append(animal)
                break
            else:
                print("Choose the correct species!")
            
            print()

        print()
        print("─"*101)
        print(f"{name}, a {species}, has born!")
        print("─"*101)
    
    
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
    def interact(pet) -> None:
        print("\n" + "="*101)
        print(f"Playing with {pet.name}, the {pet.type}:")

        while True: 

            print("\n" + "="*101)
            print("1. Feed")
            print("2. Play")
            print("3. Bath")
            print("4. Give Potion")
            print("5. Sleep")
            print("6. Take a walk")
            print("7. Talk to pet")
            print("8. Exit")
            print("─"*101)

            try:
                choice = int(input("Choose (1-8): "))
            except ValueError:
                print("\nPlease insert digit at choice input!\n")
            else:
                print()

                if (choice == 1):
                    print("─"*101)
                    print("Available food:")
                    print("─"*101 + "\n")
                    
                    for food_name in VirtualPet.list_food.keys():
                        print(f"- {food_name} (Hunger: {VirtualPet.list_food[food_name][1]}, " \
                            f"Happiness: {VirtualPet.list_food[food_name][2]}, " \
                            f"Available: {VirtualPet.list_food[food_name][0]})")
                        
                    food = input("\nWhich food (input food's name)? ").title()
                    if (food not in VirtualPet.list_food.keys()):
                        print("\nFood that you inputted doesn't exist on your fridge!")
                    else:
                        if (VirtualPet.list_food[food][0] == 0):
                            print(f"\nThere are no {food.lower()} left in the fridge!\n")
                        else:
                            pet.feed(food)
                            VirtualPet.list_food[food][0] -= 1

                elif (choice == 2):

                    if (pet.energy < 10):
                        print(f"{pet.name} is too tired to play..")
                    elif (pet.hunger < 30):
                        print(f"{pet.name} is too hungry to play..")
                    elif (pet.health < 20):
                        print(f"{pet.name} is too sick to play..")
                    else:
                        if (pet.type.lower() == "cat"):
                            print(f"You play laser with {pet.name} 💥!")
                        elif (pet.type.lower() == "rabbit"):
                            print(f"You play catch ball with {pet.name} 🥎!")
                        elif (pet.type.lower() == "dinosaur"):
                            print(f"You play hide and seek with {pet.name} 🏃!")
                        elif (pet.type.lower() == "dragon"):
                            print(f"You play fireball with {pet.name} ☄️!")
                        elif (pet.type.lower() == "pou"):
                            print(f"You brought {pet.name} to swimming pool 🏄‍♂️!")
                        
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
                        print("─"*101)

                elif (choice == 3):
                    print("─"*101)
                    print("Available soap:")
                    print("─"*101 + "\n")

                    for soap_name in VirtualPet.list_soap.keys():
                        print(f"- {soap_name} (Sanity: {VirtualPet.list_soap[soap_name][1]}, " \
                            f"Happiness: {VirtualPet.list_soap[soap_name][2]}, " \
                            f"Available: {VirtualPet.list_soap[soap_name][0]})")
                        
                    soap = input("\nWhich soap (input soap's name)? ").title()
                    if (soap not in VirtualPet.list_soap.keys()):
                        print("\nSoap that you inputted doesn't exist on your cabinet!")
                    else:
                        if (VirtualPet.list_soap[soap][0] == 0):
                            print(f"\nThere are no {soap.lower()} left in the cabinet!\n")
                        else:
                            pet.bath(soap)
                            VirtualPet.list_soap[soap][0] -= 1

                elif (choice == 4):
                    print("─"*101)
                    print("Available potions:")
                    print("─"*101 + "\n")

                    for potion_name in VirtualPet.list_potion.keys():
                        print(f"- {potion_name} (Available: {VirtualPet.list_potion[potion_name][0]})")
                        
                    potion = input("\nWhich potion (input potion's name)? ").title()
                    if (potion not in VirtualPet.list_potion.keys()):
                        print("\nPotion that you inputted doesn't exist!")
                    else:
                        if (VirtualPet.list_potion[potion][0] == 0):
                            print(f"\nThere are no {potion.lower()} left!\n")
                        else:
                            pet.health_care(potion)
                            VirtualPet.list_potion[potion][0] -= 1

                elif (choice == 5):
                    try:
                        hours = int(input(f"{pet.name}'s sleep duration (1-12): "))
                        if hours < 1 or hours > 12:
                            print("Sleep duration must between 1 to 12 hours.")
                        else:
                            pet.sleep(hours)

                    except ValueError:
                        print("Please enter a correct value.")
                
                elif (choice == 6):
                    
                    if (pet.energy < 10):
                        print(f"{pet.name} is too tired to take a walk..")
                    elif (pet.hunger < 30):
                        print(f"{pet.name} is too hungry to take a walk..")
                    elif (pet.health < 20):
                        print(f"{pet.name} is too sick to take a walk..")
                    else:
                        random_event = randrange(0,50)
                        print(f"You take {pet.name} for a walk!")

                        if (random_event == 10):
                            print("\nYou found a wallet in your way home!")
                            print("You brought back home Rp. 25,000...")
                            User.current_user.currency += 25000

                        elif (random_event == 30):
                            print("\nYour pet stepped on mud!")
                            print(f"{pet.name}' sanity decreased (-10)...")
                            pet.sanity -= 10
                        
                        elif (random_event == 20):
                            print("\nYour pet ate rotten apple!")
                            print(f"{pet.name}'s health decreased (-15)...")
                            pet.health -= 15
                        
                        elif (random_event == 4):
                            print("\nYour pet got run over by car!")
                            print(f"{pet.name} deceased... 💀\n")
                            pet.health -= 100
                            pet.limit_stat()
                            break

                        elif (random_event == 50):
                            print("\nYou got robbed on your way home!")
                            print("You lose Rp. 100,000!")
                            User.current_user.currency -= 100000
                            User.limit_currency()
                        
                        pet.happiness += 25
                        pet.hunger -= 5
                        pet.energy -= 15
                        
                        pet.limit_stat()
                        
                        print("\n" + "="*101)
                        print(f"Happiness : {pet.happiness}")
                        print(f"Hunger: {pet.hunger}")
                        print(f"Energy: {pet.energy}")
                        print("─"*101)
                    
                elif (choice == 7):

                    while True:
                        print("─"*101)
                        print("Topic of Conversation: ")
                        print("1. What do you want to do today?")
                        print("2. What is your favourite food?")
                        print("3. Can you give me money?")
                        print("4. Tell a joke")
                        print("5. Goodbye")
                        print("─"*101)
                        try:
                            topic = int(input("Choose a topic: "))
                        except ValueError:
                            print("\nPlease type a number.")
                        else:

                            if (topic == 1):
                                ans = [f"I want to eat {pet.fav_food}!", "I want to play :D", 
                                        "I want to take a walk 🌳.","I want to take a bath :)",
                                        "I want to talk to you..👉👈"]
                                rand_ans = ch(ans)
                                print(f"\n{pet.name}: {rand_ans}")

                            elif (topic == 2):
                                print(f"\n{pet.name}: My favourite food is {pet.fav_food}. :D")
                            
                            elif (topic == 3):
                                if (all(pet < 50 for pet in [pet.hunger, 
                                    pet.sanity, pet.happiness, pet.health])):
                                    print(f"\n{pet.name}: I will consider it if you take care of me properly!")
                                else:
                                    if (pet.generosity < 2):
                                        print(f"\n{pet.name}: Here, I'll give you Rp. 100,000.")
                                        User.current_user.currency += 100000
                                        pet.generosity += 1
                                    else:
                                        print(f"\n{pet.name}: Sorry, can't give you anymore... 😔")
                            
                            elif (topic == 4):
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

                                if (pet.hunger < 30):
                                    print(f"\n{pet.name} is too hungry to joke right now..")
                                elif (pet.health < 20):
                                    print(f"\n{pet.name} is too sick to joke right now..")
                                elif (pet.energy < 10):
                                    print(f"\n{pet.name} is too tired to joke right now..")
                                elif (pet.happiness < 20):
                                    print(f"\n{pet.name} is too stressed to joke right now..")
                                else:
                                    rand_jokes = ch(jokes)
                                    print(f"\n{pet.name}: {rand_jokes} Haha 🤭, funny right?")
                            
                            elif (topic == 5):
                                print(f"\n{pet.name}: Okay, goodbye!")
                                print(f"{pet.name}'s happiness has increased by 10.")
                                pet.happiness += 10
                                break
                            
                            print()

                elif (choice == 8):
                    break

                else:
                    print("\nPlease choose from (1-8).")

import datetime
from random import randrange, choice as ch
from .animal import Cat, Rabbit, Dino, Dragon, Pou, VirtualPet
from .formatter import Formatter, GARIS
from .user import User
from colorama import Fore, init
import json
init(autoreset=True)

class Game:
    def __init__(self):
        self.animal_list = []
        self.clock = datetime.datetime.now().hour
        self.format = Formatter()
        self.spend = 0
        self.day = 0
        self.jokes = []
        self.conversations = []
        self.topics_used = []
        self.load_jokes()
        self.load_conversations()
        
    def load_jokes(self):
        try:
            with open("datas/jokes.json", "r", encoding="utf-8") as f:
                self.jokes = json.load(f)
        except FileNotFoundError:
            print(Fore.RED + "Warning: datas/jokes.json not found. Jokes will not be available.")
            self.jokes = [] 
        except json.JSONDecodeError:
            print(Fore.RED + "Warning: datas/jokes.json is corrupted. Jokes will not be available.")
            self.jokes = []
    
    def load_conversations(self):
        try:
            with open("datas/conversations.json", "r", encoding="utf-8") as f:
                self.conversations = json.load(f)
        except FileNotFoundError:
            print(Fore.RED + "Warning: datas/jokes.json not found. Jokes will not be available.")
            self.conversations = [] 
        except json.JSONDecodeError:
            print(Fore.RED + "Warning: datas/jokes.json is corrupted. Jokes will not be available.")
            self.conversations = []

    @staticmethod
    def get_currency(user: User) -> int:
        return user.currency
    
    def create_name(self) -> str:
        print(Fore.RESET + "\n" + GARIS)
        name = input("Name your pet: ").title().strip()
        flag, species = self.create_species(name)
        return flag, name, species
    
    @classmethod
    def create_species(cls, name: str) -> tuple[bool, VirtualPet | None]:
        print(GARIS)
        print("Here's five types of species you can choose: ")
        print("1. Cat (🐈)")
        print("2. Rabbit (🐇)")
        print("3. Dinosaur (🦖)")
        print("4. Dragon (🐉)")
        print("5. Pou (💩)")
        print(GARIS)

        species_map = {
            "1": Cat,
            "2": Rabbit,
            "3": Dino,
            "4": Dragon,
            "5": Pou,
        }

        while True:
            species = input("Choose his/her species (1/2/3/4/5): ").strip()
            cls_type = species_map.get(species)
            if cls_type:
                animal = cls_type(name, 0)
                return True, animal
            else:
                print(Fore.RED + "\nUnknown species choice! Please try again.\n")

        
    def create(self) -> bool:
        while True:
            flag, name, species = self.create_name()

            if (species and flag):
                if not (any(animal.name == name or animal.type == species.type 
                        for animal in User.current_user.pets)):
                    self.animal_list.append((species))
                    print(Fore.GREEN + f"\nCongratulations! You have successfully" 
                        f" give birth to {name}, the {species.type}!")
                    return True
                else:
                    print(Fore.RED + f"\n{name} has been created! Please create another pet"
                            " with different name and species.\n")
                    flag = False
            
            if (not flag):
                retry = input(
                    "Would you like to create your pet again? (Y/N)\n"
                    "(Note: input other than Y and N will be considered as N): "
                ).capitalize().strip()
                
                if retry == "Y":
                    continue

                print()
                return False
            
    
    def view(self, pet) -> None:
        stats = {
            "name": pet.name, "type": pet.type, "age": f"{pet.get_age():.1f}",
            "hunger": pet.hunger, "fat": pet.fat, "sanity": pet.sanity,
            "happiness": pet.happiness, "energy": pet.energy, "health": pet.health,
            "mood": pet.get_mood(), "summary": pet.get_summary(), "age_summary": pet.get_age_summary()
        }
        print(self.format.format_status_box(stats))

    @staticmethod
    def get_health(pet) -> int:
        return pet.health
    
    @staticmethod
    def _print_main_interact_menu() -> None:
        print("="*101)
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
    def _print_stock(title: str, defs: dict, category: str, user: User) -> None:
        print("\n" + GARIS)
        print(title)
        print(GARIS + "\n")

        inv = user.inventory[category]
        is_food = category == "food"
        is_soap = category == "soap"

        for idx, (key, v) in enumerate(defs.items(), start=1):
            emoji = str(v["emoji"])
            qty = inv.get(key, 0)
            stock_text = f"{qty}" if qty > 0 else f"{Fore.RED}Out of stock{Fore.RESET}"
            if is_food:
                print(f"{idx}. {key} {emoji} (Hunger: {v['hunger']}, Happiness: {v['happiness']}, Available: {stock_text})")
            elif is_soap:
                print(f"{idx}. {key} {emoji} (Sanity: {v['sanity']}, Happiness: {v['happiness']}, Available: {stock_text})")
            else:
                print(f"{idx}. {key} {emoji} (Available: {stock_text}, Effect: {v['delta']})")
    
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
    def _food_choice_from_number(food: str) -> str | None:
        food_choice_map = {
            "1": "kentucky fried chicken", "2": "ice cream", "3": "fried rice",
            "4": "salad", "5": "french fries", "6": "mashed potato", "7": "mozarella nugget",
        }
        try:
            return food_choice_map[food].title()
        except KeyError:
            print(Fore.RED + "\nUnknown food choice! Please choose (1/2/3/4/5/6/7)!\n")

    def _feed(self, pet: VirtualPet, user: User) -> None:
        food = input("\nWhich food (1/2/3/4/5/6/7)? ").strip()
        choice = self._food_choice_from_number(food)
        if not choice:
            return
        inv = user.inventory["food"]
        if inv.get(choice, 0) <= 0:
            print(Fore.RED + f"\n{choice} is out of stock. Buy more in the shop before feeding.\n")
            return
        used = pet.feed(choice)
        if used:
            user.consume_item("food", choice, 1)
            remaining = user.inventory["food"][choice]
            emoji = str(VirtualPet.FOOD_DEF[choice]["emoji"])
            print(f"Remaining {choice} ({emoji}): {remaining}\n")

    @staticmethod
    def _play(self_pet: VirtualPet, user: User) -> None:
        pet = self_pet 
        if pet.energy < 10:
            print(Fore.RED + f"\n{pet.name} is too tired to play..\n")
            return
        if pet.hunger < 30:
            print(Fore.RED + f"\n{pet.name} is too hungry to play..\n")
            return
        if pet.health < 20:
            print(Fore.RED + f"\n{pet.name} is too sick to play..\n")
            return

        act = {
            "cat": "You play laser with", "rabbit": "You play catch ball with",
            "dinosaur": "You play hide and seek with", "dragon": "You play fireball with",
            "pou": "You brought to swimming pool"
        }.get(pet.type.lower(), "You play with")

        emoji = {
            "cat": "💥", "rabbit": "🤾", "dinosaur": "🏃", "dragon": "☄️", "pou": "🏊‍♂️"
        }.get(pet.type.lower(), "🎲")

        print(Fore.GREEN + f"\n{act} {pet.name} {emoji}!")

        pet.play()

        print(f"\n{pet.name}'s happiness increased by 10.")
        print(f"{pet.name}'s hunger decreased by 5.")
        print(f"{pet.name}'s energy decreased by 5.")
        print("You earned Rp. 25,000!")
        user.currency = user.currency + 25000

        print(Fore.YELLOW + pet.joy_upgrade_stats())

    @staticmethod
    def _soap_choice_from_number(soap: str) -> str | None:
        soap_choice_map = {
            "1": "rainbow bubble soap", "2": "pink bubble soap",
            "3": "white silk soap", "4": "flower bubble soap",
        }
        try:
            return soap_choice_map[soap].title()
        except KeyError:
            print(Fore.RED + "\nUnknown soap choice! Please choose (1/2/3/4)!\n")

    def _bath(self, pet: VirtualPet, user: User) -> None:
        soap = input("\nWhich soap (1/2/3/4)? ").strip()
        choice = self._soap_choice_from_number(soap)
        if not choice:
            return
        inv = user.inventory["soap"]
        if inv.get(choice, 0) <= 0:
            print(Fore.RED + f"\n{choice} is out of stock. Buy more in the shop before bathing.\n")
            return
        used = pet.bath(choice)
        if used:
            user.consume_item("soap", choice, 1)
            remaining = user.inventory["soap"][choice]
            emoji = str(VirtualPet.SOAP_DEF[choice]["emoji"])
            print(f"Remaining {choice} ({emoji}): {remaining}\n")

    @staticmethod
    def _potion_choice_from_number(potion: str) -> str | None:
        potion_choice_map = {
            "1": "fat burner", "2": "health potion", "3": "energizer", "4": "adult potion",
        }
        try:
            return potion_choice_map[potion].title()
        except KeyError:
            print(Fore.RED + "\nUnknown potion choice! Please choose (1/2/3/4)!\n")

    def _give_potion(self, pet: VirtualPet, user: User) -> None:
        potion = input("\nWhich potion (1/2/3/4)? ").strip()
        choice = self._potion_choice_from_number(potion)
        if not choice:
            return
        inv = user.inventory["potion"]
        if inv.get(choice, 0) <= 0:
            print(Fore.RED + f"\n{choice} is out of stock. Buy more in the shop before using.\n")
            return
        used = pet.health_care(choice)
        if used:
            user.consume_item("potion", choice, 1)
            remaining = user.inventory["potion"][choice]
            emoji = str(VirtualPet.POTION_DEF[choice]["emoji"])
            print(f"Remaining {choice} ({emoji}): {remaining}\n")

    def _sleep(self, pet: VirtualPet, user: User) -> None:

        hours = self._input_int(f"\n{pet.name}'s sleep duration (1-12): ")

        if hours is None:
            print(Fore.RED + "\nPlease insert digit at choice input!\n")
            return
        if not (1 <= hours <= 12):
            print(Fore.RED + "\nSleep duration must between 1 to 12 hours.\n")
            return
        
        pet.sleep(hours)
    
    @staticmethod
    def _walk(self_pet: VirtualPet, user: User) -> None:
        pet = self_pet
        if pet.energy < 10:
            print(Fore.RED + f"\n{pet.name} is too tired to take a walk..\n")
            return
        if pet.hunger < 30:
            print(Fore.RED + f"\n{pet.name} is too hungry to take a walk..\n")
            return
        if pet.health < 20:
            print(Fore.RED + f"\n{pet.name} is too sick to take a walk..\n")
            return

        random_event = randrange(0, 50)
        print(Fore.GREEN + f"\nYou take {pet.name} for a walk! 🐾")

        if random_event == 10:
            print(Fore.GREEN + "\nYou found a wallet in your way home!")
            print(Fore.GREEN + "You brought back home Rp. 25,000...")
            user.currency = user.currency + 25000
        elif random_event == 30:
            print(Fore.RED + "\nYour pet stepped on mud!")
            print(Fore.YELLOW + f"{pet.name}' sanity decreased (-10)...")
            pet.sanity -= 10
        elif random_event == 20:
            print(Fore.RED + "\nYour pet ate rotten apple!")
            print(Fore.YELLOW + f"{pet.name}'s health decreased (-15)...")
            pet.health -= 15
        elif random_event == 4:
            print(Fore.RED + "\nYour pet got run over by car!")
            print(Fore.RED + f"{pet.name} deceased... 💀\n")
            pet.health -= 100
            pet.limit_stat()
            return
        elif random_event == 50:
            print(Fore.RED + "\nYou got robbed on your way home!")
            print(Fore.RED + "You lose Rp. 100,000!")
            user.currency = user.currency - 100000
            user.limit_currency()

        pet.happiness += 25
        pet.hunger -= 5
        pet.energy -= 15
        
        print(f"{pet.name}'s hunger decreased by 5.")
        print(f"{pet.name}'s energy decreased by 15.")

        pet.limit_stat()

        print(Fore.YELLOW + pet.joy_upgrade_stats())
    
    def _print_talk_menu(self) -> None:
        print("\n" + GARIS)
        print("Topics of Conversation: ")
        print(GARIS)
        print("1. What do you want to do today?")
        print("2. What is your favourite food?")
        print("3. Ask me anything")
        print("4. Can you give me money?")
        print("5. Tell a joke")
        # print("6. What do you know about me?") -- COMING SOON
        print("6. Goodbye")
        print(GARIS)

    def _topic_plan(self, pet: VirtualPet, user: User) -> bool:
        ans = [
            f"I want to eat {pet.fav_food}!", "I want to play :D", 
            "I want to take a walk 🌳.","I want to take a bath :)",
            "I want to talk to you..👉👈"
        ]
        print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : {ch(ans)}")
        return True

    def _topic_fav_food(self, pet: VirtualPet, user: User) -> bool:
        print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : My favourite food is {pet.fav_food}. :D")
        return True

    def _topic_money(self, pet: VirtualPet, user: User) -> bool:
        if all(val < 50 for val in [pet.hunger, pet.sanity, pet.happiness, pet.health]):
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : I will consider it if you take care of me properly!\n")
            return False  

        if pet.generosity < 2:
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Here, I'll give you Rp. 100,000.")
            user.currency += 100000
            pet.generosity += 1
            return True  

        print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Sorry, can't give you anymore... 😔")
        return False  

    
    def _print_conversation_menu(self) -> None:
        print("\n" + GARIS)
        print("1. Music Taste")
        print("2. Favourite Food")
        # --- COMING SOON ----
        # print("3. Interest")
        # print("4. Love and Relationship")
        # print("5. Hobbies")
        # print("6. Deep Subjects")
        # print("7. Favourite Movies")
        print("3. That's enough about me")
        print(GARIS)

    def _music_topic(self, pet: VirtualPet, user: User) -> bool:
        
        if not self.conversations:
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!")
            return True
        
        music_questions = [q for q in self.conversations if q["type"] == "Music Taste"]
        
        while True:
            random_music_topics = ch(music_questions)
            
            if (random_music_topics not in self.topics_used):
                self.topics_used.append(random_music_topics)
                break
            
            if (all(music in self.topics_used for music in music_questions)):
                break
        
        ans = input(Fore.CYAN + f"\n{pet.name} {pet.emoji} : {random_music_topics.get("question","")}\n" \
                    f"{random_music_topics.get("choose","")}" + Fore.RESET).lower().strip()

        like_topic = False if "dislike" in random_music_topics.get("question") else True

        if (random_music_topics.get("answer", None) is not None):

            if (ans in random_music_topics["answer"] and like_topic):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : So, that's your fav! Mine is {pet.music_taste}.")
                User.current_user.music["Fav_Music"] = ans

            elif (ans in random_music_topics["answer"] and not like_topic):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : So, that's not your cup of tea, Mine is {pet.dislike_music}.")
                User.current_user.music["Dislike_Music"] = ans

            else:
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Not sure I've ever heard that genre, but thanks for telling me!")
                User.current_user.music["Fav_Music" if like_topic else "Dislike_Music"] = ans
        
        elif (random_music_topics.get("option", None) is not None):

            hear_spotify = True if ans == random_music_topics.get("option")[0] else False
            
            if (ans in random_music_topics["option"] and not hear_spotify):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : You should try it now! They had added your fav music playlist there!") 
                User.current_user.music["Have_Used_Spotify"] = True

            else:
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Have you heard your new fav music playlist come out there? Go check it now!")
                User.current_user.music["Have_Used_Spotify"] = False
        
        else:
            list_ans = [x.strip() for x in ans.split(",")]

            if (len(list_ans) == 3):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Owh! Mine is {", ".join(pet.songs)}.")
                User.current_user.music["Fav_Songs"] = list_ans

            else:
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : I agree too. That song almost break my heart.")
                User.current_user.music["Fav_Lyrics"] = list_ans[0]
        
        # --- In the future update, pet will remember its owner's fav music ---

        return True

    def _food_topic(self, pet: VirtualPet, user: User) -> bool:

        if not self.conversations:
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!")
            return True
        
        food_questions = [q for q in self.conversations if q["type"] == "Favourite Food/Drink"]
        
        while True:
            random_food_topics = ch(food_questions)
            
            if (random_food_topics not in self.topics_used):
                self.topics_used.append(random_food_topics)
                break

            if (all(food in self.topics_used for food in food_questions)):
                break
        
        ans = input(Fore.CYAN + f"\n{pet.name} {pet.emoji} : {random_food_topics.get("question","")}\n" + Fore.RESET).lower().strip()

        if (random_food_topics.get("option") is not None):

            flag = True if ans == random_food_topics.get("option")[0] else False

            if (ans in random_food_topics["option"] and random_food_topics.get("option")[0] == "sweet" and flag):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Owh, so you like sweet. I think you'd love Belgian Chocolate!") 
                User.current_user.food["Like_Sweet_Salty"] = ans
            
            elif (ans in random_food_topics["option"] and random_food_topics.get("option")[0] == "sweet" and not flag):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Owh, so you like salty food. I think you'd love Egg and Toast!") 
                User.current_user.food["Like_Sweet_Salty"] = ans

            elif (ans in random_food_topics["option"] and random_food_topics.get("option")[0] == "y" and not flag):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Well, International Food also tastes better!")
                User.current_user.food["Inter_Trad_Food"] = ans
            
            elif (ans in random_food_topics["option"] and random_food_topics.get("option")[0] == "y" and flag):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Our own country food is the best! I will give it a five star ⭐!")
                User.current_user.food["Inter_Trad_Food"] = ans

        else:
            if ("What is your favorite food?" in random_food_topics.get("question")):
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : That's great! My favourite food is {pet.fav_food}!")
                User.current_user.food["Fav_Food"] = ans
            else:
                print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : I'm glad to hear that! Thanks for sharing.")
            
        # --- In the future update, pet will remember its owner's fav food ---

        return True
    
    def _end_topic(self, pet: VirtualPet, user: User) -> None:
        print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Okay, I have gotten to know you more, thanks for sharing yours!")
        print(Fore.GREEN + f"{pet.name}'s happiness has increased by 10.\n")
        pet.happiness += 10

    def _topic_conversation_menu(self, pet: VirtualPet, user: User) -> bool:
        while True:
            self._print_conversation_menu()
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : What would you like to talk today? " + Fore.RESET)
            topic = self._input_int("Choose a topic: ")
            if topic is None:
                print(Fore.RED + "\nPlease type a number.")
                continue

            actions = {
                1: self._music_topic,
                2: self._food_topic,
                3: self._end_topic,
            }
            
            keep_talking = actions.get(topic, self._invalid_topic)(pet, user)
            if keep_talking is None:
                break

    def _can_tell_joke(self, pet: VirtualPet) -> tuple[bool, str | None]:
        if pet.hunger < 30:
            return False, f"\n{pet.name} is too hungry to joke right now.."
        if pet.health < 20:
            return False, f"\n{pet.name} is too sick to joke right now.."
        if pet.energy < 10:
            return False, f"\n{pet.name} is too tired to joke right now.."
        if pet.happiness < 20:
            return False, f"\n{pet.name} is too stressed to joke right now.."
        return True, None

    def _topic_joke(self, pet: VirtualPet, user: User) -> bool:
        ok, reason = self._can_tell_joke(pet)
        if not ok:
            print(Fore.RED + reason + "\n")
            return False
        
        if not self.jokes:
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : I'm all out of jokes right now! Sorry!")
            return True
        
        random_jokes = ch(self.jokes)

        ans = input(Fore.CYAN + f"\n{pet.name} {pet.emoji} : {random_jokes.get("question")} " + Fore.RESET).strip()
        
        if (ans.lower() == random_jokes.get("answer")):
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Wait! How did you know? 😱")
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : You absolutely killed the joke LOL. Great Job! 🫠")
        else:
            print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : {random_jokes.get("answer").capitalize()}! GOT YOU! 🤪")
        
        return True

    def _topic_goodbye(self, pet: VirtualPet, user: User) -> bool:
        print(Fore.CYAN + f"\n{pet.name} {pet.emoji} : Okay, goodbye!")
        print(Fore.GREEN + f"{pet.name}'s happiness has increased by 10.\n")
        pet.happiness += 10
        return False  

    @staticmethod
    def _invalid_topic(pet: VirtualPet, user: User) -> bool:
        print(Fore.RED + "\nPlease choose based on choices we have!")
        return True

    def _talk_menu(self, pet: VirtualPet, user: User) -> None:
        while True:
            self._print_talk_menu()
            topic = self._input_int("Choose a topic: ")
            if topic is None:
                print(Fore.RED + "\nPlease type a number.")
                continue

            actions = {
                1: self._topic_plan,
                2: self._topic_fav_food,
                3: self._topic_conversation_menu,
                4: self._topic_money,
                5: self._topic_joke,
                6: self._topic_goodbye,
            }
            keep_talking = actions.get(topic, self._invalid_topic)(pet, user)
            if not keep_talking and keep_talking is not None:
                break

    def _stocks(self) -> dict:
        return {
            1: ["List of Foods:", VirtualPet.FOOD_DEF, "food"],
            3: ["List of Soaps:", VirtualPet.SOAP_DEF, "soap"],
            4: ["List of Potions:", VirtualPet.POTION_DEF, "potion"],
        }

    def _actions(self):
        return {
            1: self._feed,
            2: self._play,
            3: self._bath,
            4: self._action_potion,
            5: self._sleep,
            6: self._walk,
            7: self._talk_menu,
        }

    def _action_potion(self, pet: VirtualPet, user: User) -> None:
        self._print_potion_requirement("Potion Usage Requirement")
        self._give_potion(pet, user)

    @staticmethod
    def _is_valid_choice(choice: int) -> bool:
        return 1 <= choice <= 8

    def _should_show_stock(self, choice: int) -> bool:
        return choice in self._stocks()

    def interact(self, pet, user: User) -> None:
        print(Fore.RESET + "\n" + "="*101)
        print(f"Playing with {pet.name}, the {pet.type}:".center(len(GARIS)))
        while True:
            self._print_main_interact_menu()
            choice = self._input_int("Choose (1-8): ")

            if choice is None:
                print(Fore.RED + "\nPlease enter digit!\n")
                continue

            if choice == 8:
                print()
                break

            if not self._is_valid_choice(choice):
                print(Fore.RED + "\nPlease choose from (1-8).\n")
                continue

            if self._should_show_stock(choice):
                title, defs, category = self._stocks()[choice]
                self._print_stock(title, defs, category, user)

            action = self._actions().get(choice)
            if action:
                action(pet, user)

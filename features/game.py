"""Game module: business logic for pet interactions with decoupled I/O and content loading.

This module introduces injectable I/O (InputPort/OutputPort) and content loading abstractions
to satisfy dependency inversion and remove hard-coded console/file dependencies.
"""

import datetime
from typing import Protocol, Callable, Iterable
from random import randrange, choice as ch
import json
from colorama import init
from .animal import Cat, Rabbit, Dino, Dragon, Pou, VirtualPet
from utils.formatter import Formatter
from constants.configs import LINE, NO_STOCK_MSG, FOOD_DEF, SOAP_DEF, POTION_DEF
from .user import User
from utils.colorize import red, green, yellow, cyan, reset_color

init(autoreset=True)


class InputPort(Protocol):
    """Abstract input port for reading user data."""
    def read(self, prompt: str = "") -> str: ...


class OutputPort(Protocol):
    """Abstract output port for emitting messages."""
    def write(self, message: str) -> None: ...


class ConsoleIO(InputPort, OutputPort):
    """Console-based I/O adapter used as default dependency."""
    def read(self, prompt: str = "") -> str:
        return input(prompt)

    def write(self, message: str) -> None:
        print(message)


class ContentLoader(Protocol):
    """Abstract loader for retrieving structured content."""
    def load_json(self, path: str) -> list: ...


class FileContentLoader:
    """Filesystem-based JSON content loader."""
    def load_json(self, path: str) -> list:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


class Game:
    """Main interactive game controller responsible for in-session pet interactions."""

    def __init__(
        self,
        user,
        io: InputPort | OutputPort = None,
        content_loader: ContentLoader | None = None,
    ):
        self.animal_list = []
        self.clock = datetime.datetime.now().hour
        self.format = Formatter()
        self.spend = 0
        self.day = 0
        self.jokes = []
        self.conversations = []
        self.topics_used = []
        self.io: ConsoleIO = io or ConsoleIO()
        self.content_loader = content_loader or FileContentLoader()
        self.user = user
        self.load_jokes()
        self.load_conversations()

    def load_jokes(self):
        """Load jokes data through the configured content loader."""
        try:
            self.jokes = self.content_loader.load_json("datas/jokes.json")
        except FileNotFoundError:
            self.io.write(red("Warning: datas/jokes.json not found. Jokes will not be available."))
            self.jokes = []
        except json.JSONDecodeError:
            self.io.write(red("Warning: datas/jokes.json is corrupted. Jokes will not be available."))
            self.jokes = []

    def load_conversations(self):
        """Load conversation topics through the configured content loader."""
        try:
            self.conversations = self.content_loader.load_json("datas/conversations.json")
        except FileNotFoundError:
            self.io.write(red("Warning: datas/conversations.json not found. Conversations will not be available."))
            self.conversations = []
        except json.JSONDecodeError:
            self.io.write(red("Warning: datas/conversations.json is corrupted. Conversations will not be available."))
            self.conversations = []

    def get_currency(self) -> int:
        return self.user.currency

    def create_name(self) -> tuple[bool, str, str]:
        self.io.write(reset_color("\n" + LINE))
        name = self.io.read("Name your pet: ").title().strip()
        flag, species = self.create_species(name)
        return flag, name, species

    @classmethod
    def create_species(cls, name: str) -> tuple[bool, VirtualPet | None]:
        """Prompt species selection and create the chosen pet."""
        def print_menu(out: Callable[[str], None]) -> None:
            out(LINE)
            out("Here's five types of species you can choose: ")
            out("1. Cat (🐈)")
            out("2. Rabbit (🐇)")
            out("3. Dinosaur (🦖)")
            out("4. Dragon (🐉)")
            out("5. Pou (💩)")
            out(LINE)

        io = ConsoleIO()
        print_menu(io.write)

        species_map = {
            "1": Cat,
            "2": Rabbit,
            "3": Dino,
            "4": Dragon,
            "5": Pou,
        }

        while True:
            species = io.read("Choose his/her species (1/2/3/4/5): ").strip()
            cls_type = species_map.get(species)
            if cls_type:
                animal = cls_type(name, 0)
                return True, animal
            else:
                io.write(red("\nUnknown species choice! Please try again.\n"))

    def create(self) -> bool:
        """High-level pet creation flow combining name and species selection."""
        while True:
            flag, name, species = self.create_name()

            if (species and flag):
                if not any(animal.name == name for animal in User.current_user.pets):
                    self.animal_list.append((species))
                    self.io.write(green(f"\nCongratulations! You have successfully give birth to {name}, the {species.type}!"))
                    return True
                else:
                    self.io.write(red(f"\n{name} has been created! Please create another pet with different name and species.\n"))
                    flag = False

            if (not flag):
                retry = self.io.read(
                    "Would you like to create your pet again? (Y/N)\n"
                    "(Note: input other than Y and N will be considered as N): "
                ).capitalize().strip()

                if retry == "Y":
                    continue

                self.io.write("")
                return False

    def view(self, pet) -> None:
        """Render a pet's status using the Formatter helper."""
        stats = {
            "name": pet.name, "type": pet.type, "age": f"{pet.get_age():.1f}",
            "hunger": pet.hunger, "fat": pet.fat, "sanity": pet.sanity,
            "happiness": pet.happiness, "energy": pet.energy, "health": pet.health,
            "mood": pet.get_mood(), "summary": pet.get_summary(), "age_summary": pet.get_age_summary()
        }
        self.io.write(self.format.format_status_box(stats))

    @staticmethod
    def get_health(pet) -> int:
        return pet.health

    @staticmethod
    def _render_lines(items: Iterable[str]) -> str:
        """Join lines for menu rendering."""
        return "\n".join(items)

    def _print_main_interact_menu(self) -> None:
        menu = [
            "="*120,
            "1. Feed",
            "2. Play",
            "3. Bath",
            "4. Give Potion",
            "5. Sleep",
            "6. Take a walk",
            "7. Talk to pet",
            "8. Exit",
            LINE,
        ]
        self.io.write(self._render_lines(menu))

    @staticmethod
    def _input_int(prompt: str, reader: InputPort):
        """Read integer input safely via provided reader."""
        try:
            return int(reader.read(prompt))
        except ValueError:
            return None

    def _print_stock(self, title: str, defs: dict, category: str) -> None:
        """Render inventory stock listing for a category."""
        lines = ["", LINE, title, LINE + "\n"]
        inv = self.user.inventory[category]
        is_food = category == "food"
        is_soap = category == "soap"

        for idx, (key, v) in enumerate(defs.items(), start=1):
            emoji = str(v["emoji"])
            qty = inv.get(key, 0)
            stock_text = f"{qty}" if qty > 0 else f"{red(NO_STOCK_MSG)}"
            if is_food:
                lines.append(f"{idx}. {key} {emoji} (Hunger: {v['hunger']}, Happiness: {v['happiness']}, Available: {stock_text})")
            elif is_soap:
                lines.append(f"{idx}. {key} {emoji} (Sanity: {v['sanity']}, Happiness: {v['happiness']}, Available: {stock_text})")
            else:
                lines.append(f"{idx}. {key} {emoji} (Available: {stock_text}, Effect: {v['delta']})")
        self.io.write("\n".join(lines))

    def _print_potion_requirement(self, title: str) -> None:
        """Display potion usage requirements."""
        lines = [
            "",
            LINE,
            title,
            LINE,
            "1. Fat Burner can be used if your energy is below 50.",
            "2. Health Potion can be used if your health is below 100.",
            "3. Energizer can be used if your energy is below 100.",
            "4. Adult Potion can be used if your age is below 20.",
            LINE + "\n",
        ]
        self.io.write("\n".join(lines))

    @staticmethod
    def _food_choice_from_number(food: str) -> str | None:
        """Translate menu index to food name."""
        food_choice_map = {
            "1": "kentucky fried chicken", "2": "ice cream", "3": "fried rice",
            "4": "salad", "5": "french fries", "6": "mashed potato", "7": "mozarella nugget",
        }
        try:
            return food_choice_map[food].title()
        except KeyError:
            ConsoleIO().write(red("\nUnknown food choice! Please choose (1/2/3/4/5/6/7)!\n"))

    def _feed(self, pet: VirtualPet) -> None:
        """Handle feeding action using user inventory."""
        food = self.io.read("\nWhich food (1/2/3/4/5/6/7)? ").strip()
        choice = self._food_choice_from_number(food)
        if not choice:
            return
        inv = self.user.inventory["food"]
        if inv.get(choice, 0) <= 0:
            self.io.write(red(f"\n{choice} is {NO_STOCK_MSG}. Buy more in the shop before feeding.\n"))
            return
        used = pet.feed(choice)
        if used:
            self.user.consume_item("food", choice, 1)
            remaining = self.user.inventory["food"][choice]
            emoji = str(FOOD_DEF[choice]["emoji"])
            self.io.write(f"Remaining {choice} ({emoji}): {remaining}\n")

    def _play(self, self_pet: VirtualPet) -> None:
        """Play interaction that adjusts pet stats and user currency."""
        pet = self_pet
        if pet.energy < 10:
            self.io.write(red(f"\n{pet.name} is too tired to play..\n"))
            return
        if pet.hunger < 30:
            self.io.write(red(f"\n{pet.name} is too hungry to play..\n"))
            return
        if pet.health < 20:
            self.io.write(red(f"\n{pet.name} is too sick to play..\n"))
            return

        act = {
            "cat": "You play laser with", "rabbit": "You play catch ball with",
            "dinosaur": "You play hide and seek with", "dragon": "You play fireball with",
            "pou": "You brought to swimming pool"
        }.get(pet.type.lower(), "You play with")

        emoji = {
            "cat": "💥", "rabbit": "🤾", "dinosaur": "🏃", "dragon": "☄️", "pou": "🏊‍♂️"
        }.get(pet.type.lower(), "🎲")

        self.io.write(green(f"\n{act} {pet.name} {emoji}!"))

        pet.play()

        self.io.write(f"\n{pet.name}'s happiness increased by 10.")
        self.io.write(f"{pet.name}'s hunger decreased by 5.")
        self.io.write(f"{pet.name}'s energy decreased by 5.")
        self.io.write("You earned Rp. 25,000!")
        self.user.currency = self.user.currency + 25000

        self.io.write(yellow(pet.joy_upgrade_stats()))

    @staticmethod
    def _soap_choice_from_number(soap: str) -> str | None:
        """Translate menu index to soap name."""
        soap_choice_map = {
            "1": "rainbow bubble soap", "2": "pink bubble soap",
            "3": "white silk soap", "4": "flower bubble soap",
        }
        try:
            return soap_choice_map[soap].title()
        except KeyError:
            ConsoleIO().write(red("\nUnknown soap choice! Please choose (1/2/3/4)!\n"))

    def _bath(self, pet: VirtualPet) -> None:
        """Handle bathing action using user inventory."""
        soap = self.io.read("\nWhich soap (1/2/3/4)? ").strip()
        choice = self._soap_choice_from_number(soap)
        if not choice:
            return
        inv = self.user.inventory["soap"]
        if inv.get(choice, 0) <= 0:
            self.io.write(red(f"\n{choice} is {NO_STOCK_MSG}. Buy more in the shop before bathing.\n"))
            return
        used = pet.bath(choice)
        if used:
            self.user.consume_item("soap", choice, 1)
            remaining = self.user.inventory["soap"][choice]
            emoji = str(SOAP_DEF[choice]["emoji"])
            self.io.write(f"Remaining {choice} ({emoji}): {remaining}\n")

    @staticmethod
    def _potion_choice_from_number(potion: str) -> str | None:
        """Translate menu index to potion name."""
        potion_choice_map = {
            "1": "fat burner", "2": "health potion", "3": "energizer", "4": "adult potion",
        }
        try:
            return potion_choice_map[potion].title()
        except KeyError:
            ConsoleIO().write(red("\nUnknown potion choice! Please choose (1/2/3/4)!\n"))

    def _give_potion(self, pet: VirtualPet) -> None:
        """Handle potion usage with validation."""
        potion = self.io.read("\nWhich potion (1/2/3/4)? ").strip()
        choice = self._potion_choice_from_number(potion)
        if not choice:
            return
        inv = self.user.inventory["potion"]
        if inv.get(choice, 0) <= 0:
            self.io.write(red(f"\n{choice} is {NO_STOCK_MSG}. Buy more in the shop before using.\n"))
            return
        used = pet.health_care(choice)
        if used:
            self.user.consume_item("potion", choice, 1)
            remaining = self.user.inventory["potion"][choice]
            emoji = str(POTION_DEF[choice]["emoji"])
            self.io.write(f"Remaining {choice} ({emoji}): {remaining}\n")

    def _sleep(self, pet: VirtualPet) -> None:
        """Handle sleep interaction with bounds checking."""
        hours = self._input_int(f"\n{pet.name}'s sleep duration (1-12): ", self.io)

        if hours is None:
            self.io.write(red("\nPlease insert digit at choice input!\n"))
            return
        if not (1 <= hours <= 12):
            self.io.write(red("\nSleep duration must between 1 to 12 hours.\n"))
            return

        pet.sleep(hours)

    def _walk(self, self_pet: VirtualPet) -> None:
        """Handle walk interaction with random events."""
        pet = self_pet
        if pet.energy < 10:
            self.io.write(red(f"\n{pet.name} is too tired to take a walk..\n"))
            return
        if pet.hunger < 30:
            self.io.write(red(f"\n{pet.name} is too hungry to take a walk..\n"))
            return
        if pet.health < 20:
            self.io.write(red(f"\n{pet.name} is too sick to take a walk..\n"))
            return

        random_event = randrange(0, 50)
        self.io.write(green(f"\nYou take {pet.name} for a walk! 🐾"))
        if random_event == 10:
            self.io.write(green("\nYou found a wallet in your way home!"))
            self.io.write(green("You brought back home Rp. 25,000..."))
            self.user.currency = self.user.currency + 25000
        elif random_event == 30:
            self.io.write(red("\nYour pet stepped on mud!"))
            self.io.write(yellow(f"{pet.name}'s sanity decreased (-10)..."))
            pet.sanity -= 10
        elif random_event == 20:
            self.io.write(red("\nYour pet ate rotten apple!"))
            self.io.write(yellow(f"{pet.name}'s health decreased (-15)..."))
            pet.health -= 15
        elif random_event == 4:
            self.io.write(red("\nYour pet got run over by car!"))
            self.io.write(red(f"{pet.name} deceased... 💀\n"))
            pet.health -= 100
            pet.limit_stat()
            return
        elif random_event == 50:
            self.io.write(red("\nYou got robbed on your way home!"))
            self.io.write(red("You lose Rp. 100,000!"))
            self.user.currency = self.user.currency - 100000
            self.user.limit_currency()

        pet.happiness += 25
        pet.hunger -= 5
        pet.energy -= 15

        self.io.write(f"{pet.name}'s hunger decreased by 5.")
        self.io.write(f"{pet.name}'s energy decreased by 15.")

        pet.limit_stat()

        self.io.write(yellow(pet.joy_upgrade_stats()))

    def _print_talk_menu(self) -> None:
        """Render top-level talk topics menu."""
        lines = [
            "\n" + LINE,
            "Topics of Conversation: ",
            LINE,
            "1. What do you want to do today?",
            "2. What is your favourite food?",
            "3. Ask me anything",
            "4. Can you give me money?",
            "5. Tell a joke",
            "6. Goodbye",
            LINE,
        ]
        self.io.write("\n".join(lines))

    def _topic_plan(self, pet: VirtualPet) -> bool:
        """Plan topic handler."""
        ans = [
            f"I want to eat {pet.fav_food}!", "I want to play :D",
            "I want to take a walk 🌳.", "I want to take a bath :)",
            "I want to talk to you..👉👈"
        ]
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : {ch(ans)}"))
        return True

    def _topic_fav_food(self, pet: VirtualPet) -> bool:
        """Favourite food topic handler."""
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : My favourite food is {pet.fav_food}. :D"))
        return True

    def _topic_money(self, pet: VirtualPet) -> bool:
        """Money request topic handler with generosity gating."""
        if all(val < 50 for val in [pet.hunger, pet.sanity, pet.happiness, pet.health]):
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I will consider it if you take care of me properly!\n"))
            return False

        if pet.generosity < 2:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Here, I'll give you Rp. 100,000."))
            self.user.currency += 100000
            pet.generosity += 1
            return True

        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Sorry, can't give you anymore... 😔\n"))
        return False

    def _print_conversation_menu(self) -> None:
        """Render conversation subtopics."""
        lines = [
            "\n" + LINE,
            "1. Music Taste",
            "2. Favourite Food",
            "3. That's enough about me",
            LINE,
        ]
        self.io.write("\n".join(lines))

    def _music_topic(self, pet: VirtualPet) -> bool:
        """Handle music-related conversation topics."""
        if not self.conversations:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!"))
            return False

        music_questions = [q for q in self.conversations if q["type"] == "Music Taste"]

        if not music_questions:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I don't have any music topics right now! Sorry!"))
            return False

        random_music_topics = self._select_unused_topic(music_questions)

        question = random_music_topics.get('question', '')
        choose_text = random_music_topics.get('choose', '')
        ans = self.io.read(cyan(f"\n{pet.name} {pet.emoji} : {question}\n{choose_text}")).lower().strip()

        like_topic = "dislike" not in question

        if random_music_topics.get("answer") is not None:
            self._handle_answer_type(pet, random_music_topics, ans, like_topic)

        elif random_music_topics.get("option") is not None:
            self._handle_option_type(pet, random_music_topics, ans)

        else:
            self._handle_list_type(pet, ans)

        return True

    def _select_unused_topic(self, questions: list) -> dict:
        """Return a random unused topic, cycling when exhausted."""
        while True:
            random_topic = ch(questions)

            if random_topic not in self.topics_used:
                self.topics_used.append(random_topic)
                break

            if all(q in self.topics_used for q in questions):
                break

        return random_topic

    def _handle_answer_type(self, pet: VirtualPet, topic: dict, ans: str, like_topic: bool) -> None:
        """Process free-text answers with validation list."""
        is_valid_answer = ans in topic.get("answer", [])

        if is_valid_answer and like_topic:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : So, that's your fav! Mine is {getattr(pet, 'music_taste', 'unknown')}."))
            User.current_user.music["Fav_Music"] = ans

        elif is_valid_answer and not like_topic:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : So, that's not your cup of tea, Mine is {getattr(pet, 'dislike_music', 'unknown')}."))
            User.current_user.music["Dislike_Music"] = ans

        else:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Not sure I've ever heard that genre, but thanks for telling me!"))
            key = "Fav_Music" if like_topic else "Dislike_Music"
            User.current_user.music[key] = ans

    def _handle_option_type(self, pet: VirtualPet, topic: dict, ans: str) -> None:
        """Process option-based music topics."""
        first_option = topic.get("option")[0]
        is_first_option = ans == first_option
        is_valid_option = ans in topic.get("option", [])

        if is_valid_option and not is_first_option:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : You should try it now! They had added your fav music playlist there! "))
            User.current_user.music["Have_Used_Spotify"] = True
        else:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Have you heard your new fav music playlist come out there?  Go check it now!"))
            User.current_user.music["Have_Used_Spotify"] = False

    def _handle_list_type(self, pet: VirtualPet, ans: str) -> None:
        """Process list-style music responses."""
        list_ans = [x.strip() for x in ans.split(",")]

        if len(list_ans) == 3:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Owh! Mine is {', '.join(getattr(pet, 'songs', []))}."))
            User.current_user.music["Fav_Songs"] = list_ans
        else:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I agree too. That song almost break my heart."))
            User.current_user.music["Fav_Lyrics"] = list_ans[0] if list_ans else ""

    def _food_topic(self, pet: VirtualPet) -> bool:
        """Handle food-related conversation topics."""
        if not self.conversations:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of topics right now! Sorry!"))
            return False

        food_questions = [q for q in self.conversations if q["type"] == "Favourite Food/Drink"]

        if not food_questions:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I don't have any food topics right now! Sorry!"))
            return False

        random_food_topics = self._select_unused_topic(food_questions)

        ans = self.io.read(cyan(f"\n{pet.name} {pet.emoji} : {random_food_topics.get('question','')}\n")).lower().strip()

        if random_food_topics.get("option") is not None:
            self._handle_food_option_type(pet, random_food_topics, ans)
        else:
            self._handle_food_free_response(pet, random_food_topics, ans)

        return True

    def _handle_food_option_type(self, pet: VirtualPet, topic: dict, ans: str) -> None:
        """Process option-based food topics."""
        first_option = topic.get("option")[0]
        is_first_option = ans == first_option
        is_valid_option = ans in topic.get("option", [])

        if not is_valid_option:
            return

        if first_option == "sweet":
            self._handle_sweet_salty_preference(pet, ans, is_first_option)
        elif first_option == "y":
            self._handle_food_origin_preference(pet, ans, is_first_option)

    def _handle_sweet_salty_preference(self, pet: VirtualPet, ans: str, is_sweet: bool) -> None:
        """Record sweet/salty preference."""
        if is_sweet:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Owh, so you like sweet. I think you'd love Belgian Chocolate! "))
            User.current_user.food["Like_Sweet_Salty"] = ans
        else:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Owh, so you like salty food. I think you'd love Egg and Toast!"))
            User.current_user.food["Like_Sweet_Salty"] = ans

    def _handle_food_origin_preference(self, pet: VirtualPet, ans: str, is_traditional: bool) -> None:
        """Record international vs traditional preference."""
        if is_traditional:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Our own country food is the best! I will give it a five star ⭐!"))
            User.current_user.food["Inter_Trad_Food"] = ans
        else:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Well, International Food also tastes better!"))
            User.current_user.food["Inter_Trad_Food"] = ans

    def _handle_food_free_response(self, pet: VirtualPet, topic: dict, ans: str) -> None:
        """Record free-form food preferences."""
        if "What is your favorite food?" in topic.get("question", ""):
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : That's great! My favourite food is {pet.fav_food}!"))
            User.current_user.food["Fav_Food"] = ans
        else:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm glad to hear that! Thanks for sharing."))

    def _end_topic(self, pet: VirtualPet) -> None:
        """End conversation and boost happiness."""
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Okay, I have gotten to know you more, thanks for sharing yours!"))
        self.io.write(green(f"{pet.name}'s happiness has increased by 10."))
        pet.happiness += 10

    def _topic_conversation_menu(self, pet: VirtualPet) -> bool:
        """Conversation sub-loop for selected topics."""
        while True:
            self._print_conversation_menu()
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : What would you like to talk today? "))
            topic = self._input_int("Choose a topic: ", self.io)
            if topic is None:
                self.io.write(red("\nPlease type a number."))
                continue

            actions = {
                1: self._music_topic,
                2: self._food_topic,
                3: self._end_topic,
            }

            keep_talking = actions.get(topic, self._invalid_topic)(pet)
            if keep_talking is None:
                break

    def _can_tell_joke(self, pet: VirtualPet) -> tuple[bool, str | None]:
        """Check whether pet is in condition to tell a joke."""
        if pet.hunger < 30:
            return False, f"\n{pet.name} is too hungry to joke right now.."
        if pet.health < 20:
            return False, f"\n{pet.name} is too sick to joke right now.."
        if pet.energy < 10:
            return False, f"\n{pet.name} is too tired to joke right now.."
        if pet.happiness < 20:
            return False, f"\n{pet.name} is too stressed to joke right now.."
        return True, None

    def _topic_joke(self, pet: VirtualPet) -> bool:
        """Handle joke topic with optional stored punchline."""
        ok, reason = self._can_tell_joke(pet)
        if not ok:
            self.io.write(red(reason + "\n"))
            return False

        if not self.jokes:
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm all out of jokes right now! Sorry!"))
            return True

        random_jokes = ch(self.jokes)

        question = random_jokes.get('question', '')
        answer_expected = random_jokes.get('answer', '')
        ans = self.io.read(cyan(f"\n{pet.name} {pet.emoji} : {question} ")).strip()

        if (ans.lower() == (answer_expected or "").lower()):
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Wait! How did you know? 😱"))
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : You absolutely killed the joke LOL. Great Job! 🫠"))
        else:
            resp = (answer_expected.capitalize() if answer_expected else "No punchline")
            self.io.write(cyan(f"\n{pet.name} {pet.emoji} : {resp}! GOT YOU! 🤪"))

        return True

    def _topic_goodbye(self, pet: VirtualPet) -> bool:
        """Goodbye topic handler."""
        self.io.write(cyan(f"\n{pet.name} {pet.emoji} : Okay, goodbye!"))
        self.io.write(green(f"{pet.name}'s happiness has increased by 10.\n"))
        pet.happiness += 10
        return False

    def _invalid_topic(self) -> bool:
        """Fallback for invalid topic selection."""
        self.io.write(red("\nPlease choose based on choices we have!"))
        return True

    def _talk_menu(self, pet: VirtualPet) -> None:
        """Top-level conversation menu loop."""
        while True:
            self._print_talk_menu()
            topic = self._input_int("Choose a topic: ", self.io)
            if topic is None:
                self.io.write(red("\nPlease type a number."))
                continue

            actions = {
                1: self._topic_plan,
                2: self._topic_fav_food,
                3: self._topic_conversation_menu,
                4: self._topic_money,
                5: self._topic_joke,
                6: self._topic_goodbye,
            }
            action = actions.get(topic)

            if action is None:
                self._invalid_topic()
                continue

            keep_talking = action(pet)
            if not keep_talking:
                break

    def _stocks(self) -> dict:
        """Return stock metadata keyed by menu selection."""
        return {
            1: ["List of Foods:", FOOD_DEF, "food"],
            3: ["List of Soaps:", SOAP_DEF, "soap"],
            4: ["List of Potions:", POTION_DEF, "potion"],
        }

    def _actions(self):
        """Return mapping of menu choices to action handlers."""
        return {
            1: self._feed,
            2: self._play,
            3: self._bath,
            4: self._action_potion,
            5: self._sleep,
            6: self._walk,
            7: self._talk_menu,
        }

    def _action_potion(self, pet: VirtualPet) -> None:
        """Print potion requirements then execute potion flow."""
        self._print_potion_requirement("Potion Usage Requirement")
        self._give_potion(pet)

    @staticmethod
    def _is_valid_choice(choice: int) -> bool:
        """Validate main interaction choice range."""
        return 1 <= choice <= 8

    def _should_show_stock(self, choice: int) -> bool:
        """Check if stock display is needed for given choice."""
        return choice in self._stocks()

    def interact(self, pet) -> None:
        """Main loop for interacting with a specific pet and executing chosen actions."""
        self.io.write(reset_color("\n" + "="*120))
        self.io.write(f"Playing with {pet.name}, the {pet.type}:".center(len(LINE)))
        while True:
            self._print_main_interact_menu()
            choice = self._input_int("Choose (1-8): ", self.io)

            if choice is None:
                self.io.write(red("\nPlease enter digit!\n"))
                continue

            if (choice == 8) or (pet.health == 0):
                self.io.write("")
                break

            if not self._is_valid_choice(choice):
                self.io.write(red("\nPlease choose from (1-8).\n"))
                continue

            if self._should_show_stock(choice):
                title, defs, category = self._stocks()[choice]
                self._print_stock(title, defs, category)

            action = self._actions().get(choice)
            if action:
                action(pet)
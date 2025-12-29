from .baseClass import MinigameStrategy
import time
from random import choice, randint, random
from constants.configs import LINE
from utils.formatter import clear
from utils.colorize import green
from colorama import init

init(autoreset=True)

class MemoryMatch(MinigameStrategy):
    """Memorize-and-recall game using digits, words or mixed tokens."""

    name = "Memory Match"

    def load_words(self):
        with open("datas/words.txt") as word_file:
            words = list(word_file.read().split())
        return words

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.sequence = []
        self.user_response = []
        self.length = None
        self.charset = "words"
        self.start_time = None
        self.end_time = None
        self.difficulty = 0
        self.words = self.load_words()

    def display_menu(self):
        """Explain Memory Match rules and difficulty levels."""
        print("\n" + LINE)
        print("🧩 Memory Match 🧩")
        print(LINE)
        print("Memorize a short sequence, then reproduce it.")
        print("Faster and more accurate answers give better rewards.")
        print(LINE)
        print("Choose difficulty:")
        print(LINE)
        print("1. Easy   (sequence length 5-6, digits)")
        print("2. Medium (sequence length 3-4, words)")
        print("3. Hard   (sequence length 6-8, mixed digits/words)")
        print(LINE)

    def get_input(self):
        """Collect difficulty choice."""
        try:
            diff = int(input("Choose difficulty (1-3): ").strip())
        except ValueError:
            diff = 1
        if diff not in range(1, 4):
            diff = 1
        self.difficulty = diff

    def build_question(self):
        """Build the sequence to memorize based on difficulty and charset."""
        diff = self.difficulty
        if diff == 1:
            self.length = choice([5, 6])
            self.charset = "digits"
        elif diff == 2:
            self.length = choice([3, 4])
            self.charset = "words"
        else:
            self.length = choice([6, 7, 8])
            self.charset = "mixed"

        if self.charset == "digits":
            self.sequence = [str(randint(0, 9)) for _ in range(self.length)]
        elif self.charset == "words":
            for _ in range(self.length):
                self.sequence.append(choice(self.words))
        else:
            self.sequence = []
            for _ in range(self.length):
                if random() < 0.6:
                    self.sequence.append(str(randint(0, 9)))
                else:
                    self.sequence.append(choice(self.words))

    def build_game(self):
        """Show the sequence briefly and then prompt the player to reproduce it."""
        print("\n" + LINE)
        print("Game started!")
        print(LINE)
        print("Memorize this sequence:")
        print(" ".join(self.sequence))
        time.sleep(1.0 + 0.5 * self.length)
        clear()
        print("Now type the sequence separated by spaces (e.g. \"1 2 3\" or \"cat dog 5\" or \"cat dog fruit\").")
        ans = input("Your answer: ").strip()
        ans_list = ans.split()
        return ans_list

    def evaluate(self, answer):
        """Compare the user's response to the expected sequence and count correct items."""
        self.user_response = answer
        correct = 0
        for expected, ans in zip(self.sequence, self.user_response):
            if expected == ans:
                correct += 1
        total = len(self.sequence)
        exact = (correct == total) and (len(self.user_response) == total)

        user_stats = {
            "correct": correct,
            "total": total,
            "exact": exact,
            "sequence": self.sequence,
            "response": self.user_response,
        }

        return user_stats

    def reward(self, result):
        """Compute rewards and print a summary for MemoryMatch."""
        correct = int(result.get("correct", 0))
        total = int(result.get("total", 1))
        exact = bool(result.get("exact", False))
        coins = correct * int(self.difficulty)

        if exact and total > 0:
            coins += (5 * int(self.difficulty))

        pet_happiness = correct // int(self.difficulty) if self.difficulty else correct

        print("\n" + LINE)
        print("RESULT".center(len(LINE)))
        print(LINE)
        print(f"Sequence was: {' '.join(result['sequence'])}")
        print(f"Your response: {' '.join(result['response']) if result['response'] else '(none)'}")
        print(f"\nCorrect: {correct}/{total}")
        if exact:
            print(green("Perfect! Bonus awarded! 🎉"))
        print(f"You earned Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})\n")
        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        """Run the MemoryMatch flow and return rewards."""
        self.setup(player, pet)
        self.display_menu()
        self.get_input()
        self.build_question()
        answer = self.build_game()
        result = self.evaluate(answer)
        return self.reward(result)

"""
minigame/memory_match.py

Memory Match minigame.

Behavior is preserved. This refactor introduces a small dependency boundary for
loading words to support DIP without changing any game rules.
"""

import time
from random import choice, randint, random
from typing import Protocol, Sequence

from constants.configs import UIConfig as UIC
from utils.colorize import green
from utils.formatter import clear
from utils.ports import ConsoleIO, InputPort, OutputPort

from .base_class import MinigameStrategy


class WordSource(Protocol):
    """Abstraction for retrieving word tokens used by MemoryMatch."""
    def load_words(self) -> Sequence[str]: ...


class FileWordSource:
    """Default WordSource that reads datas/words.txt exactly as before."""
    def __init__(self, path: str = "datas/words.txt"):
        self._path = path

    def load_words(self) -> Sequence[str]:
        with open(self._path) as word_file:
            return list(word_file.read().split())


class MemoryMatch(MinigameStrategy):
    """Memorize-and-recall game using digits, words or mixed tokens."""

    name = "Memory Match"

    def __init__(
        self,
        io: InputPort | OutputPort | None = None,
        word_source: WordSource | None = None,
    ):
        self.io: InputPort | OutputPort = io or ConsoleIO()
        self._word_source: WordSource = word_source or FileWordSource()

    def load_words(self):
        # Preserve the original method and behavior; now delegated.
        return list(self._word_source.load_words())

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
        self.io.write("\n" + UIC.LINE)
        self.io.write("🧩 Memory Match 🧩")
        self.io.write(UIC.LINE)
        self.io.write("Memorize a short sequence, then reproduce it.")
        self.io.write("Faster and more accurate answers give better rewards.")
        self.io.write(UIC.LINE)
        self.io.write("Choose difficulty:")
        self.io.write(UIC.LINE)
        self.io.write("1. Easy   (sequence length 5-6, digits)")
        self.io.write("2. Medium (sequence length 3-4, words)")
        self.io.write("3. Hard   (sequence length 6-8, mixed digits/words)")
        self.io.write(UIC.LINE)

    def get_input(self):
        """Collect difficulty choice."""
        try:
            diff = int(self.io.read("Choose difficulty (1-3): ").strip())
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
        self.io.write("\n" + UIC.LINE)
        self.io.write("Game started!")
        self.io.write(UIC.LINE)
        self.io.write("Memorize this sequence:")
        self.io.write(" ".join(self.sequence))
        time.sleep(1.0 + 0.5 * self.length)
        clear()
        self.io.write('Now type the sequence separated by spaces (e.g. "1 2 3" or "cat dog 5" or "cat dog fruit").')
        ans = self.io.read("Your answer: ").strip()
        return ans.split()

    def evaluate(self, answer):
        """Compare the user's response to the expected sequence and count correct items."""
        self.user_response = answer
        correct = 0
        for expected, ans in zip(self.sequence, self.user_response):
            if expected == ans:
                correct += 1
        total = len(self.sequence)
        exact = (correct == total) and (len(self.user_response) == total)

        return {
            "correct": correct,
            "total": total,
            "exact": exact,
            "sequence": self.sequence,
            "response": self.user_response,
        }

    def reward(self, result):
        """Compute rewards and print a summary for MemoryMatch."""
        correct = int(result.get("correct", 0))
        total = int(result.get("total", 1))
        exact = bool(result.get("exact", False))
        coins = correct * int(self.difficulty)

        if exact and total > 0:
            coins += (5 * int(self.difficulty))

        pet_happiness = correct // int(self.difficulty) if self.difficulty else correct

        self.io.write("\n" + UIC.LINE)
        self.io.write("RESULT".center(len(UIC.LINE)))
        self.io.write(UIC.LINE)
        self.io.write(f"Sequence was: {' '.join(result['sequence'])}")
        self.io.write(f"Your response: {' '.join(result['response']) if result['response'] else '(none)'}")
        self.io.write(f"\nCorrect: {correct}/{total}")
        if exact:
            self.io.write(green("Perfect! Bonus awarded! 🎉"))
        self.io.write(f"You earned Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})\n")
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
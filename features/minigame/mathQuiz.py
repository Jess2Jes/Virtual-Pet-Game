import operator
import time
from random import randint, choice
from .baseClass import MinigameStrategy
from utils.colorize import yellow
from typing import Any, Dict
from constants.configs import LINE
from colorama import init

init(autoreset=True)

class MathQuiz(MinigameStrategy):
    """A short arithmetic quiz where speed and accuracy determine rewards."""

    name = "Math Quiz"

    ARITHMETIC_OPERATIONS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": lambda a, b: a // b if b != 0 else 0,
        "%": operator.mod,
        "**": operator.pow
    }

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.questions = []
        self.answers = []
        self.correct = 0
        self.start_time = None
        self.end_time = None
        self.difficulty = None

    def display_menu(self):
        """Explain rules and difficulty options to the player."""
        print("\n" + LINE)
        print("➕ Math Quiz ➗")
        print(LINE)
        print("🔍 This game is created to test your logical thinking skill! 🔍")
        print("🧠 Answer the given arithmetic questions as fast and accurately as you can... 🤓")
        print("You will get your coin rewards and boost your pet's happiness! 😸")
        print(LINE)
        print("Before we start, please choose your difficulty: ")
        print(LINE)
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Master")
        print(LINE)
        print("NOTE: Any user's input other than 1-4 will be considered 1 (Default: Difficulty Easy)")
        print(LINE)

    def get_input(self):
        """Collect difficulty choice (1-4)."""
        try:
            diff = int(input("Choose your difficulty (1-4): ").strip())
        except ValueError:
            diff = 1
        if diff not in range(1, 5):
            diff = 1
        self.difficulty = diff

    def build_question(self):
        """Generate the arithmetic questions based on chosen difficulty."""
        if self.difficulty == 1:
            total_question = 5
            max_value = 10
            operators = ["+", "-"]
        elif self.difficulty == 2:
            total_question = 10
            max_value = 30
            operators = ["+", "-", "*", "/"]
        elif self.difficulty == 3:
            total_question = 20
            max_value = 50
            operators = ["+", "-", "*", "/", "**"]
        elif self.difficulty == 4:
            total_question = 20
            max_value = 60
            operators = ["+", "-", "*", "/", "%", "**"]

        for _ in range(total_question):
            a = randint(1, max_value)
            b = randint(1, max_value)
            op = choice(operators)
            if op == "/":
                b = randint(1, max(1, max_value // randint(1, max(1, max_value - 1))))
                a = b * randint(1, max(1, max_value // max(1, b)))
            elif op == "**":
                b = randint(1, max(1, max_value // 10))
            self.questions.append((a, op, b))

    def build_game(self):
        """Prompt the user with all questions and collect integer answers (None for invalid)."""
        print(yellow(f"\nYou will be asked {len(self.questions)} questions. Type your answer (must be an int): "))
        print(LINE)
        self.start_time = time.time()
        user_answers = []
        for i, (a, op, b) in enumerate(self.questions, start=1):
            try:
                ans = int(input(f"Q{i}: {a} {op} {b} = ").strip())
            except ValueError:
                ans = None
            user_answers.append(ans)
        self.end_time = time.time()
        return user_answers

    def evaluate(self, user_answers):
        """Evaluate provided answers against expected results and compute accuracy/timing metrics."""
        for (a, op, b), u in zip(self.questions, user_answers):
            func = self.ARITHMETIC_OPERATIONS.get(op)
            if func:
                expected = func(a, b)
            else:
                expected = None
            self.answers.append(expected)
            # Note: this check treats expected==0 as falsy; preserving original logic.
            if expected and u == expected:
                self.correct += 1
        elapsed = max(0.001, self.end_time - self.start_time) if self.start_time and self.end_time else 0.0
        accuracy = self.correct / len(self.questions) if self.questions else 0.0
        user_stats = {
            "correct": self.correct,
            "total": len(self.questions),
            "elapsed": elapsed,
            "accuracy": accuracy,
            "answers": self.answers,
            "user_answers": user_answers
        }
        return user_stats

    def reward(self, result):
        """Compute currency and pet happiness rewards from the evaluation result."""
        correct = result.get("correct", 0)
        total = result.get("total", 1)
        diff = self.difficulty if hasattr(self, "difficulty") else 1
        time_penalty = int(result.get("elapsed", 0) // 5)
        coins = max(0, correct * 5 * diff - time_penalty)
        pet_happiness = correct

        # fixed quoting for nested keys
        elapsed = result.get("elapsed", 0)
        accuracy = result.get("accuracy", 0.0)
        print(f"\nResult: {correct}/{total} correct in {elapsed:.2f}s (accuracy {round(accuracy * 100)}%)")
        print(f"You earned Rp. {'{:,}'.format(coins * 1000)} and your pet gains {pet_happiness} happiness.")
        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        """Run the full MathQuiz lifecycle and return rewards dict."""
        self.setup(player, pet)
        self.display_menu()
        self.get_input()
        self.build_question()
        answer = self.build_game()
        result = self.evaluate(answer)
        reward = self.reward(result)
        return reward
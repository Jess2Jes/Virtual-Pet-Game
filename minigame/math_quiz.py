"""Math Quiz minigame implementation (conforms to MinigameStrategy interfaces)."""

import time
from random import randint, choice
from typing import Any, Dict
from .base_class import MinigameStrategy
from utils.ports import ConsoleIO, InputPort, OutputPort
from utils.colorize import yellow
from constants.configs import UIConfig as UIC , MathConfig as MATHC


class MathQuiz(MinigameStrategy):
    """A short arithmetic quiz where speed and accuracy determine rewards."""
    name = "Math Quiz"

    def __init__(self, io: InputPort | OutputPort | None = None):
        self.io: InputPort | OutputPort = io or ConsoleIO()

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
        self.io.write("\n" + UIC.LINE)
        self.io.write("➕ Math Quiz ➗")
        self.io.write(UIC.LINE)
        self.io.write("🔍 This game is created to test your logical thinking skill! 🔍")
        self.io.write("🧠 Answer the given arithmetic questions as fast and accurately as you can... 🤓")
        self.io.write("You will get your coin rewards and boost your pet's happiness! 😸")
        self.io.write(UIC.LINE)
        self.io.write("Before we start, please choose your difficulty: ")
        self.io.write(UIC.LINE)
        self.io.write("1. Easy")
        self.io.write("2. Medium")
        self.io.write("3. Hard")
        self.io.write("4. Master")
        self.io.write(UIC.LINE)
        self.io.write("NOTE: Any user's input other than 1-4 will be considered 1 (Default: Difficulty Easy)")
        self.io.write(UIC.LINE)

    def get_input(self):
        """Collect difficulty choice (1-4)."""
        try:
            diff = int(self.io.read("Choose your difficulty (1-4): ").strip())
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
        else:
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
        self.io.write(yellow(f"\nYou will be asked {len(self.questions)} questions. Type your answer (must be an int): "))
        self.io.write(UIC.LINE)
        self.start_time = time.time()
        user_answers = []
        for i, (a, op, b) in enumerate(self.questions, start=1):
            try:
                ans = int(self.io.read(f"Q{i}: {a} {op} {b} = ").strip())
            except ValueError:
                ans = None
            user_answers.append(ans)
        self.end_time = time.time()
        return user_answers

    def evaluate(self, user_answers):
        """Evaluate provided answers against expected results and compute accuracy/timing metrics."""
        for (a, op, b), u in zip(self.questions, user_answers):
            func = MATHC.OPERATIONS.get(op)
            expected = func(a, b) if func else None
            self.answers.append(expected)
            if expected and u == expected:
                self.correct += 1
        elapsed = max(0.001, self.end_time - self.start_time) if self.start_time and self.end_time else 0.0
        accuracy = self.correct / len(self.questions) if self.questions else 0.0
        return {
            "correct": self.correct,
            "total": len(self.questions),
            "elapsed": elapsed,
            "accuracy": accuracy,
            "answers": self.answers,
            "user_answers": user_answers
        }

    def reward(self, result):
        """Compute currency and pet happiness rewards from the evaluation result."""
        correct = result.get("correct", 0)
        total = result.get("total", 1)
        diff = self.difficulty if hasattr(self, "difficulty") else 1
        time_penalty = int(result.get("elapsed", 0) // 5)
        coins = max(0, correct * 5 * diff - time_penalty)
        pet_happiness = correct

        elapsed = result.get("elapsed", 0)
        accuracy = result.get("accuracy", 0.0)
        self.io.write(f"\nResult: {correct}/{total} correct in {elapsed:.2f}s (accuracy {round(accuracy * 100)}%)")
        self.io.write(f"You earned Rp. {'{:,}'.format(coins * 1000)} and your pet gains {pet_happiness} happiness.")
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
from __future__ import annotations
from typing import Any, Dict, List, Tuple
from abc import ABC, abstractmethod
from random import randint, choice, random, shuffle
import time
import operator
import string

from constants.configs import LINE
from utils.colorize import yellow, red, green, blue
from utils.formatter import clear
from .user import User
from colorama import init

init(autoreset=True)


"""
minigame.py

Contains a small minigame framework and several concrete games used by the Virtual Pet Game.

Key classes:
- MinigameStrategy: abstract base that all minigames implement.
- MathQuiz, TicTacToe, MemoryMatch, BattleContest: concrete minigame implementations.
- MinigameEngine: registry and dispatcher for available minigames.

Each minigame implements a simple lifecycle:
- setup(player, pet): prepare state from the player and pet
- display_menu(): show rules/prompts
- get_input()/build_question()/build_game(): collect parameters and run the interactive flow
- evaluate(result)/reward(result): compute rewards to apply to the player/pet
- play(player, pet): convenience to run the full flow and return rewards dict

Notes:
- This module is console-driven (input()/print()). It was documented and a few small
  syntactic issues were corrected (extra spaces in attribute access, incorrect Fore attribute usage,
  and an f-string quoting issue). Game logic itself was preserved.
"""

class MinigameStrategy(ABC):
    """Abstract base class for minigame implementations."""

    name: str

    @abstractmethod
    def setup(self, player: Any, pet: Any) -> None:
        """Prepare internal state before the game begins."""
        pass

    @abstractmethod
    def display_menu(self) -> None:
        """Show a description and choices to the player."""
        pass

    @abstractmethod
    def get_input(self) -> Any:
        """Collect any initial input from the player (difficulty, options, etc.)."""
        pass

    @abstractmethod
    def build_question(self) -> Any:
        """Build the questions or game board prior to playing."""
        pass

    @abstractmethod
    def build_game(self) -> Any:
        """Run the interactive portion where the user provides answers/moves."""
        pass

    @abstractmethod
    def evaluate(self, answer: Any) -> Dict[str, Any]:
        """Evaluate the raw answers/moves and return a structured result."""
        pass

    @abstractmethod
    def reward(self, result: Dict[str, Any]) -> Dict[str, int]:
        """Convert evaluation results into currency/pet happiness rewards."""
        pass

    @abstractmethod
    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        """High-level convenience that runs the full minigame flow and returns rewards."""
        pass


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


class TicTacToe(MinigameStrategy):
    """n x n Tic-Tac-Toe with an AI pet opponent and configurable board sizes."""

    name = "Tic Tac Toe"

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.row_length = 3
        self.col_length = 3
        self.board = [[" " for _ in range(self.col_length)] for _ in range(self.row_length)]
        self.player_mark = "X"
        self.pet_mark = "O"
        self.first = True
        self.winner = None
        self.difficulty = 1
        self.win_length = 3

    def display_menu(self):
        """Show rules and rewards for the Tic Tac Toe minigame."""
        print("\n" + LINE)
        print("⭕ Tic Tac Toe ✖️")
        print(LINE)
        print("Let's play classic Tic-Tac-Toe with your pet!")
        print("You are X, your pet is O.")
        print(LINE)
        print("Win ---> more currency")
        print("Draw ---> small currency")
        print("Loss ---> no currency")
        print(LINE)

    def build_question(self):
        """Collect board-size choice and prepare an empty board."""
        print(yellow("Choose the size of your Tic Tac Toe board!"))
        print(LINE)
        print("1. 3 x 3 board")
        print("2. 4 x 4 board")
        print("3. 5 x 5 board")
        print(LINE)
        try:
            diff = int(input("Choose your size of board (1/2/3): ").strip())
        except ValueError:
            diff = 1
        if diff not in range(1, 4):
            diff = 1
        self.difficulty = diff
        if self.difficulty == 1:
            length = 3
            self.win_length = 3
        elif self.difficulty == 2:
            length = 4
            self.win_length = 4
        else:
            length = 5
            self.win_length = 5

        self.row_length = length
        self.col_length = length
        self.board = [[" " for _ in range(self.col_length)] for _ in range(self.row_length)]

    def render_board(self):
        """Render the current board to the console."""
        print()
        print("   " + " ".join(f"{c+1:3}" for c in range(self.col_length)))
        print("  +" + "---+" * self.col_length)
        for r in range(self.row_length):
            row_cells = " | ".join(self.board[r][c] if self.board[r][c] != " " else " " for c in range(self.col_length))
            print(f"{r+1:2}| {row_cells} |")
            print("  +" + "---+" * self.col_length)
        print()

    def available_moves(self):
        """Return list of empty cells as (row, col) tuples."""
        available: List[Tuple[int, int]] = []
        for i in range(self.row_length):
            for j in range(self.col_length):
                if self.board[i][j] == " ":
                    available.append((i, j))
        return available

    def get_input(self):
        """Ask if the player wants to play first (Y/N)."""
        while True:
            choice = input("\nDo you want to play first (Y/N)? ").strip().lower()
            if choice == "y":
                self.first = True
                break
            elif choice == "n":
                self.first = False
                break
            print(red("Please answer Y/N!"))

    def check_winner(self):
        """Check the board for winning sequences in all directions and return counts per mark."""
        counts = {}

        # Check all four directions
        self._check_horizontal_wins(counts)
        self._check_vertical_wins(counts)
        self._check_diagonal_wins(counts)
        self._check_anti_diagonal_wins(counts)

        return counts

    def _check_horizontal_wins(self, counts: dict) -> None:
        """Check for horizontal winning sequences."""
        for row in range(self.row_length):
            for col in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 0, 1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_vertical_wins(self, counts: dict) -> None:
        """Check for vertical winning sequences."""
        for col in range(self.col_length):
            for row in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, 0, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_diagonal_wins(self, counts: dict) -> None:
        """Check for diagonal winning sequences (top-left to bottom-right)."""
        for row in range(self.row_length - self.win_length + 1):
            for col in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, 1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_anti_diagonal_wins(self, counts: dict) -> None:
        """Check for anti-diagonal winning sequences (top-right to bottom-left)."""
        for row in range(self.row_length - self.win_length + 1):
            for col in range(self.win_length - 1, self.col_length):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, -1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _is_winning_sequence(self, start_row: int, start_col: int,
                            row_delta: int, col_delta: int, mark: str) -> bool:
        """Check if there's a winning sequence starting from given position."""
        if mark == " ":
            return False

        for offset in range(self.win_length):
            row = start_row + offset * row_delta
            col = start_col + offset * col_delta
            if self.board[row][col] != mark:
                return False

        return True

    def make_move(self, row, col, mark):
        """Place a mark at row,col if valid and empty."""
        if (0 <= row < self.row_length) and (0 <= col < self.col_length) and (self.board[row][col] == " "):
            self.board[row][col] = mark
            return True
        return False

    def winning_move(self, mark):
        """Return a winning move (row, col) for mark if available, otherwise None."""
        for row, col in self.available_moves():
            self.board[row][col] = mark
            winner = self.check_winner()
            self.board[row][col] = " "
            if winner.get(mark, 0) > 0:
                return row, col
        return None

    def pet_move(self):
        """Compute the pet's move using heuristics: win, block, fork, center, corners, edges."""
        if len(self.available_moves()) == self.row_length * self.col_length:
            center = (self.row_length // 2, self.col_length // 2)
            if center in self.available_moves():
                return center

            corners = [(0, 0), (0, self.col_length - 1), (self.row_length - 1, 0),
                       (self.row_length - 1, self.col_length - 1)]
            for corner in corners:
                if corner in self.available_moves():
                    return corner

        win = self.winning_move(self.pet_mark)
        if win:
            return win

        block = self.winning_move(self.player_mark)
        if block:
            return block

        fork_move = self.fork_move(self.pet_mark)
        if fork_move:
            return fork_move

        block_fork = self.fork_move(self.player_mark)
        if block_fork:
            return block_fork

        center = (self.row_length // 2, self.col_length // 2)
        if center in self.available_moves():
            return center

        corners = [(0, 0), (0, self.col_length - 1), (self.row_length - 1, 0),
                   (self.row_length - 1, self.col_length - 1)]
        for corner in corners:
            if corner in self.available_moves():
                return corner

        if self.row_length >= 4:
            edges = []

            for c in range(1, self.col_length - 1):
                if (0, c) in self.available_moves():
                    edges.append((0, c))
                if (self.row_length - 1, c) in self.available_moves():
                    edges.append((self.row_length - 1, c))

            for r in range(1, self.row_length - 1):
                if (r, 0) in self.available_moves():
                    edges.append((r, 0))
                if (r, self.col_length - 1) in self.available_moves():
                    edges.append((r, self.col_length - 1))

            if edges:
                best_edge = self.best_edge(edges)
                if best_edge:
                    return best_edge

        return choice(self.available_moves())

    def fork_move(self, mark):
        """Attempt to find a move that creates multiple immediate winning threats (fork)."""
        best_move = None
        max_forks = 0

        for move in self.available_moves():
            self.board[move[0]][move[1]] = mark

            fork_count = 0
            for test_move in self.available_moves():
                self.board[test_move[0]][test_move[1]] = mark
                wins = self.check_winner()

                if wins.get(mark, 0) > 0:
                    fork_count += 1

                self.board[test_move[0]][test_move[1]] = " "

            self.board[move[0]][move[1]] = " "

            if fork_count > max_forks:
                max_forks = fork_count
                best_move = move

        if max_forks >= 2:
            return best_move

        return None

    def best_edge(self, edges):
        """Select the best edge cell from a list using simple heuristics (varies by board size)."""
        if self.row_length == 4:

            best_score = -1
            best_edge = None

            for edge in edges:
                row_distance = abs(edge[0] - (self.row_length // 2))
                col_distance = abs(edge[1] - (self.col_length // 2))

                score = 2 - (row_distance + col_distance)

                self.board[edge[0]][edge[1]] = self.pet_mark
                likely_wins = 0

                for test_move in self.available_moves():
                    self.board[test_move[0]][test_move[1]] = self.pet_mark
                    wins = self.check_winner()

                    if wins.get(self.pet_mark, 0) > 0:
                        likely_wins += 1
                    self.board[test_move[0]][test_move[1]] = " "

                self.board[edge[0]][edge[1]] = " "

                score += likely_wins * 0.5

                if score > best_score:
                    best_score = score
                    best_edge = edge

            return best_edge

        elif self.row_length == 5:
            best_edge = None

            for edge in edges:
                self.board[edge[0]][edge[1]] = self.pet_mark
                winning_move = self.winning_move(self.pet_mark)
                self.board[edge[0]][edge[1]] = " "

                if winning_move:
                    return edge

                center_distance = float('inf')

                for e in edges:
                    distance = abs(e[0] - 2) + abs(e[1] - 2)

                    if distance < center_distance:
                        center_distance = distance
                        best_edge = e

            return best_edge

        return edges[0] if edges else None

    def player_move(self):
        """Prompt the player for a row/column move and validate it."""
        print("\n" + LINE)
        print("It's your turn! Pick your cell now!")
        print(LINE)
        try:
            row, col = map(int, input(f"\nEnter row (1-{self.row_length}) and column (1-{self.col_length}) --> ex: 2 3: ").strip().split())
            row -= 1
            col -= 1
        except ValueError:
            print(red("Please input two numbers separated by space (e.g. '2 3')."))
            return None
        if row < 0 or row >= self.row_length:
            print(red(f"Row number cannot be less than 1 or more than {self.row_length}!"))
            return None
        if col < 0 or col >= self.col_length:
            print(red(f"Column number cannot be less than 1 or more than {self.col_length}!"))
            return None
        if (row, col) not in self.available_moves():
            print(yellow("Cell has been placed with mark!"))
            return None

        return row, col

    def count_sequence(self):
        """Render board, count winning sequences and determine winner mark by majority."""
        self.render_board()
        counts = self.check_winner()
        player = counts.get(self.player_mark, 0)
        pet = counts.get(self.pet_mark, 0)
        if player > pet:
            winner = self.player_mark
        elif pet > player:
            winner = self.pet_mark
        else:
            winner = None

        return winner

    def build_game(self):
        """Run the main turn loop until the board is finished or no moves left."""
        player_turn = self.first

        while True:
            self.render_board()

            if player_turn:
                self._execute_player_turn()
            else:
                self._execute_pet_turn()

            if self._check_game_over():
                break

            player_turn = not player_turn

        return {"winner": self.winner}

    def _execute_player_turn(self) -> None:
        """Handle the player's turn."""
        move = None
        while move is None:
            move = self.player_move()
        row, col = move
        self.make_move(row, col, self.player_mark)

    def _execute_pet_turn(self) -> None:
        """Handle the pet's turn."""
        row, col = self.pet_move()
        self.make_move(row, col, self.pet_mark)
        print(f"Pet placed '{self.pet_mark}' at (row-{row + 1} col-{col + 1}).")

    def _check_game_over(self) -> bool:
        """Check if the game has ended and set the winner."""
        if (self.win_length <= 4) and (self.row_length < 4):
            if self.check_winner():
                self.render_board()
                self.winner = self.count_sequence()
                return True

        if self.row_length >= 3:
            if not self.available_moves():
                self.render_board()
                self.winner = self.count_sequence()
                return True

        return False

    def evaluate(self, summary):
        """Convert the raw summary into a result outcome string."""
        winner = summary.get("winner")
        if winner == self.player_mark:
            outcome = "Win"
        elif winner == self.pet_mark:
            outcome = "Lose"
        else:
            outcome = "Draw"
        return {"outcome": outcome}

    def reward(self, result):
        """Translate outcome into currency and pet happiness and display a summary."""
        outcome = result.get("outcome")
        if outcome == "Win":
            coins = 20
            pet_happiness = 0
            print("\nYou win! 🎉")
        elif outcome == "Draw":
            coins = 5
            pet_happiness = 2
            print("\nIt's a draw!")
        else:
            coins = 0
            pet_happiness = 5
            print("\nYou lose.. 🥲")
        print("Your pet is having fun playing with you!")
        print(f"Reward: Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})")
        print(green(f"You received Rp. {'{:,}'.format(coins * 1000)} 🎉"))
        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        """Run an entire TicTacToe game and return rewards."""
        self.setup(player, pet)
        self.display_menu()
        self.build_question()
        self.get_input()
        summary = self.build_game()
        result = self.evaluate(summary)
        reward = self.reward(result)
        return reward


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


class BattleContest(MinigameStrategy):
    """Simple multi-round pet-battle simulation against another player's pet."""

    name = "Battle Tournament"

    def setup(self, player, pet):
        self.player = player
        self.player_pet = pet
        self.player_pet_stats = {
            "strength": 15,
            "agility": 10
        }
        self.current_round = 1
        self.player_health = self.player_pet.health * 1000
        self.player_won = 0
        other_players_with_pets = list(filter(lambda user: user != self.player and user.pets, User.users.values()))
        if other_players_with_pets:
            self.opponent = choice(other_players_with_pets)
            self.opponent_pet = choice(self.opponent.pets)
        else:
            print(red("\nOther players currently doesn't have any pets yet!\n"))
            return False
        self.opponent_health = self.opponent_pet.health * 1000
        self.opponent_won = 0
        self.opponent_pet_stats = {
            "strength": 25,
            "agility": 15
        }
        self.player_heal_count = 0
        self.player_heal_limit = 3
        self.opponent_heal_count = 0
        self.opponent_heal_limit = 5
        return True

    def display_menu(self):
        """Display battle status and available actions for the current round."""
        print("\n" + LINE)
        print(f"PET BATTLE TOURNAMENT -> ROUND - {self.current_round}".center(len(LINE)))
        print(LINE)
        print("\n" + LINE)
        print(f"Your Pet: {self.player_pet.name}")
        print(f"Health: {self.player_health}")
        print(f"Strength: {self.player_pet_stats['strength']}")
        print(f"Agility: {self.player_pet_stats['agility']}")
        print('-' * len(LINE))

        if self.opponent_pet:
            print(f"Opponent: {self.opponent_pet.name}")
            print(f"Health: {self.opponent_health}")
            print(f"Strength: {self.player_pet_stats['strength']}")
            print(f"Agility: {self.player_pet_stats['agility']}")

        print(LINE)
        print("\nBattle Options:")
        print(LINE)
        print("1. Attack 🗡️")
        print("2. Defend 🛡️")
        print("3. Special Move ✨")
        print("4. Heal ❤️‍🩹")
        print(LINE)

    def get_input(self):
        """Prompt and validate a numeric choice for the battle action."""
        while True:
            try:
                choice = int(input("Choose your action (1-4): "))
                if 1 <= choice <= 4:
                    return choice
                else:
                    print(red("Please enter a number between 1-4!"))
            except ValueError:
                print(red("Please enter a valid number!"))

    def build_question(self) -> Any:
        """Prepare the battle sequence and announce start."""
        print("\n" + LINE)
        print("Battle Starting!")
        print(LINE)
        print(f"{self.player_pet.name} VS {self.opponent_pet.name}")
        print("Prepare for battle!")
        time.sleep(2)

    def build_game(self) -> Any:
        """Main battle loop: alternate player/opponent actions until one health reaches 0."""
        while self.opponent_health > 0 and self.player_health > 0:
            self.display_menu()
            player_choice = self.get_input()

            self._execute_player_action(player_choice)
            self._execute_opponent_action()

            self.current_round += 1
            time.sleep(1)

        self._determine_battle_outcome()

        battle_result = {
            "player_health": max(0, self.player_health),
            "opponent_health": max(0, self.opponent_health),
            "player_won": (self.player_won > self.opponent_won),
            "rounds_played": self.current_round
        }

        return battle_result

    def _execute_player_action(self, choice: int) -> None:
        """Execute the player's chosen action."""
        if choice == 1:
            self._player_attack()
        elif choice == 2:
            self._player_defend()
        elif choice == 3:
            self._player_special_move()
        elif choice == 4:
            self._player_heal()

    def _execute_opponent_action(self) -> None:
        """Execute the opponent's action chosen at random."""
        opponent_choice = randint(1, 4)

        if opponent_choice == 1:
            self._opponent_attack()
        elif opponent_choice == 2:
            self._opponent_defend()
        elif opponent_choice == 3:
            self._opponent_special_move()
        elif opponent_choice == 4:
            self._opponent_heal()

    def _player_attack(self) -> None:
        """Player attacks the opponent."""
        damage = (randint(5, 10) + self.player_pet_stats["strength"] // 3) * 300
        self.opponent_health -= damage
        print(f"\n{self.player_pet.name} attacks for {damage} damage ⚔️!")

    def _player_defend(self) -> None:
        """Player defends, temporarily reducing incoming damage (display only)."""
        defense_bonus = randint(2, 5) * 3000
        print(f"\n{self.player_pet.name} defends 🛡️!")
        print(f"Damage reduction: {defense_bonus}")

    def _player_special_move(self) -> None:
        """Player uses special move (only on even rounds)."""
        if self.current_round % 2 == 0:
            special_damage = (randint(10, 15) + self.player_pet_stats["strength"] // 2) * 600
            self.opponent_health -= special_damage
            print(f"\n{self.player_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            print(red("\nSpecial moves are locked in odd rounds!"))

    def _player_heal(self) -> None:
        """Player heals if heal limit not exceeded."""
        if self.player_heal_count < self.player_heal_limit:
            heal_amount = randint(8, 12) * 500
            self.player_health += heal_amount
            print(f"\n{self.player_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.player_heal_count += 1
        else:
            print(red("\nYou already healed 3 times!"))

    def _opponent_attack(self) -> None:
        """Opponent attacks the player."""
        damage = (randint(4, 8) + self.opponent_pet_stats["strength"] // 3) * 300
        self.player_health -= damage
        print(f"{self.opponent_pet.name} attacks for {damage} damage ⚔️!")

    def _opponent_defend(self) -> None:
        """Opponent defends (display only)."""
        defense_bonus = randint(1, 4) * 3000
        print(f"{self.opponent_pet.name} defends 🛡️!")
        print(f"Damage reduction: {defense_bonus}")

    def _opponent_special_move(self) -> None:
        """Opponent special move (only on odd rounds)."""
        if self.current_round % 2 != 0:
            special_damage = (randint(8, 12) + self.opponent_pet_stats["strength"] // 2) * 600
            self.player_health -= special_damage
            print(f"{self.opponent_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            print(red("\nOpponent's special moves are restricted on even rounds!"))

    def _opponent_heal(self) -> None:
        """Opponent heals if heal limit not exceeded."""
        if self.opponent_heal_count < self.opponent_heal_limit:
            heal_amount = randint(6, 10) * 500
            self.opponent_health += heal_amount
            print(f"{self.opponent_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.opponent_heal_count += 1
        else:
            print(red("\nOpponent's healing ability are restricted to 5 times only!"))

    def _determine_battle_outcome(self) -> None:
        """Determine and display the battle outcome and update counters."""
        if self.opponent_health <= 0:
            print(f"{self.opponent_pet.name} was defeated 🎉!")
            self.player_won += 1
            self.current_round += 1

        if self.player_health <= 0:
            print(f"{self.player_pet.name} was defeated 🎉!")
            self.opponent_won += 1

        if self.player_health <= 0 and self.opponent_health <= 0:
            print("It's a draw! 🤺")

    def evaluate(self, answer):
        """Construct a richer evaluation dict from raw battle results."""
        battle_result = answer
        player_won = battle_result.get("player_won", False)
        player_health = battle_result.get("player_health", 0)
        opponent_health = battle_result.get("opponent_health", 0)

        evaluation = {
            "victory": player_won,
            "player_health_remaining": player_health,
            "opponent_health_remaining": opponent_health,
            "performance_score": min(100, (player_health * 3) + (50 if player_won else 0)),
            "battle_ended": (player_health <= 0 or opponent_health <= 0)
        }

        return evaluation

    def reward(self, result):
        """Compute and print battle rewards based on performance and outcome."""
        victory = bool(result.get("victory", False))
        performance_score = int(result.get("performance_score", 0))
        player_health_remaining = int(result.get("player_health_remaining", 0))

        coins = 0
        pet_happiness = 0

        if victory:
            coins = 20 + (performance_score // 10)
            pet_happiness = 15 + ((player_health_remaining - 1000) // 5)
            print(green(f"🎉 VICTORY! {self.player_pet.name} won the battle!"))
        else:
            coins = 5 + (performance_score // 20)
            pet_happiness = 5 + ((player_health_remaining - 1000) // 10)
            print(red(f"💔 Defeat... {self.player_pet.name} was defeated."))
        print("\n" + LINE)
        print("BATTLE RESULTS")
        print(LINE)
        print(f"Performance Score: {performance_score}/100")
        print(f"Health Remaining: {player_health_remaining}")
        print(f"Coins Earned: {'{:,}'.format(coins * 1000)}")
        print(f"Pet Happiness: (+{pet_happiness})")
        print(LINE)

        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        """Run the battle contest flow and return rewards (if setup succeeds)."""
        res = self.setup(player, pet)
        if res:
            self.build_question()
            battle_result = self.build_game()
            evaluation = self.evaluate(battle_result)
            return self.reward(evaluation)

class Sudoku(MinigameStrategy):
    """A simple Sudoku minigame where logic-base determine rewards."""

    name = "Sudoku"

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.difficulty = 1
        self.cell_removed = 35
        self.grid = [[0] * 9 for _ in range(9)]
        self.pre_filled = [[False] * 9 for _ in range(9)]
        self.tries = 3
        self.coins = 50
    
    @staticmethod
    def display_menu():
        """Show rules and rewards for the Sudoku minigame."""
        print("\n" + LINE)
        print("🔢 Sudoku 🔢")
        print(LINE)
        print("Let's play classic Sudoku with your pet!")
        print("You must complete following sudoku in order to win the game!")
        print(LINE)
        print("Rules on Sudoku: ")
        print("1. Use number in range 1-9 (Do not exceed this range!)")
        print("2. Do not repeat any numbers (no repeating in rows, columns and grid 3 x 3)")
        print("3. You only have 3 tries to solve the sudoku")
        print(LINE)
        print("Win ---> more currency")
        print("Loss ---> better luck next time")
        print(LINE)
    
    def build_question(self):
        """Collect difficulty choice and prepare an incomplete Sudoku."""
        print(yellow("Level of Difficulty: "))
        print(LINE)
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Expert")
        print(LINE)
        try:
            diff = int(input("Choose your difficulty (1/2/3/4): ").strip())
        except ValueError:
            diff = 1
        if diff not in range(1, 5):
            diff = 1
        self.difficulty = diff
        if self.difficulty == 1:
            self.cell_removed = 35
        elif self.difficulty == 2:
            self.cell_removed = 45
        elif self.difficulty == 3:
            self.cell_removed = 55
        else:
            self.cell_removed = 65
    
    def print_grid(self):
        """Display the Sudoku grid with coordinates"""
        print("\n    1 2 3   4 5 6   7 8 9")
        print("  +-------+-------+-------+")
        for i, row in enumerate(self.grid):
            if i > 0 and i % 3 == 0:
                print("  +-------+-------+-------+")
            print(f"{i + 1} |", end='')
            for j, num in enumerate(row):
                if j > 0 and j % 3 == 0:
                    print(" |", end='')
                if self.pre_filled[i][j]:
                    print(f" {num}", end='')
                elif self.grid[i][j] != 0:
                    print(f" {num}", end='')
                else:
                    print("  ", end="")
            print(" |")
        print("  +-------+-------+-------+")
        print()
    
    @staticmethod
    def is_valid(board, row, col, num):
        """Check if placing num at (row, col) is valid"""
        # Check row for any duplicates
        for i in range(9):
            if board[row][i] == num:
                return False
        
        # Check column for any duplicates
        for i in range(9):
            if board[i][col] == num:
                return False
        
        # Check 3x3 subgrid for any duplicates
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False
                
        # If there is no duplicates in any
        return True

    def solve_sudoku(self, board):
        """Solve Sudoku using backtracking algorithm"""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    numbers = list(range(1, 10))
                    shuffle(numbers)
                    for num in numbers:
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            if self.solve_sudoku(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def generate_sudoku(self):
        """Generate a Sudoku puzzle with given difficulty"""

        temp_grid = [row[:] for row in self.grid]
        # Complete Solution of Sudoku
        self.solve_sudoku(temp_grid)

        for i in range(9):
            for j in range(9):
                self.grid[i][j] = temp_grid[i][j]

        positions = [(r, c) for r in range(9) for c in range(9)]
        shuffle(positions)

        for i in range(self.cell_removed):
            row, col = positions[i]
            self.grid[row][col] = 0

        for row in range(9):
            for col in range(9):
                if self.grid[row][col] != 0:
                    self.pre_filled[row][col] = True
    
    def get_input(self):
        """Get and validate user input"""
        while True:
            choice = input("Enter Move: ").strip().lower()

            if choice in ['exit', 'quit', 'q', 'ex', 'e']:
                return 'exit', None

            if choice == 'hint':
                return 'hint', None
            
            if choice.startswith('clear '):
                parts = choice.split()
                if len(parts) == 2:
                    position = parts[1]
                    if len(position) == 2 and position[0] in string.digits and position[1] in string.digits:
                        row, col = int(position[0]) - 1, int(position[1]) - 1
                        if not self.pre_filled[row][col]:
                            return 'clear', (row, col)
                        else:
                            print(red('Cannot clear a pre-filled cell!\n'))
                            continue

                print(red("Invalid clear command. Use format: 'clear 11'.\n"))
                continue

            parts = choice.replace(',', '').split()
            if len(parts) != 2:
                print(red('Invalid input. Use format: 11 5 (col)(row) (value)\n'))
                continue

            position, number = parts[0], parts[1]
            if len(position) != 2 or position[0] not in string.digits or position[1] not in string.digits:
                print(red("Invalid position. Use format like 11, 23, etc.\n"))
                continue

            try:
                number = int(number)
                if number < 1 or number > 9:
                    print(red('Number must be between 1 and 9.\n'))
                    continue
            except ValueError:
                print(red('Invalid number. Please enter a number between 1 and 9.\n'))
                continue

            row, col = int(position[0]) - 1, int(position[1]) - 1
            return 'move', (row, col, number)
    
    def get_hint(self):
        empty_cells = [(r, c) for r in range(9) for c in range(9) if self.grid[r][c] == 0]
        if empty_cells:
            row, col = choice(empty_cells)
            temp_grid = [row[:] for row in self.grid]
            self.solve_sudoku(temp_grid)
            self.coins -= 15
            return f"Try placing {temp_grid[row][col]} at col-{row + 1} row-{col + 1}."
        return "No hints available - puzzle is complete!"
    
    def build_game(self):
        difficulty_map = {1: "easy", 2: "medium", 3: "hard", 4: "expert"}
        difficulty = difficulty_map[self.difficulty]
        print(f"\nStarting '{difficulty.capitalize()}' level puzzle...")
        self.generate_sudoku()
        solution = [row[:] for row in self.grid]
        self.solve_sudoku(solution)

        print("\nInstructions:")
        print("- Enter moves as 'column-row number' (e.g., '11 5')")
        print("- Type 'hint' for a suggestion")
        print("- Type 'clear 11' to clear a cell")
        print("- Type 'q', 'quit', or 'exit' to quit")

        self.print_grid()
        moves = 0
        solved = False

        while True:
            print(yellow(f"Tries remaining: ({self.tries}/3)"))
            action, data = self.get_input()
            if action == 'exit':
                print(yellow("\nYou exited."))
                return solved

            elif action == 'hint':
                hint = self.get_hint()
                print(blue(f"\n 💡 Hint: {hint}\n"))
                continue

            elif action == 'clear':
                row, col = data
                if self.grid[row][col] != 0:
                    self.grid[row][col] = 0
                    print(green(f"\nCleared col-{col + 1} row-{row + 1}."))
                    self.print_grid()
                else:
                    print(red("Cell is already empty!\n"))
                continue

            elif action == 'move':
                row, col, num = data
                if self.pre_filled[row][col]:
                    print(red(f"Cell {col + 1}{row + 1} is pre-filled with {self.grid[row][col]}. Try a different cell.\n"))
                    continue

                temp_value = self.grid[row][col]
                self.grid[row][col] = 0

                if self.is_valid(self.grid, row, col, num):
                    self.grid[row][col] = num
                    moves += 1
                    print(green(f"\nPlaced {num} at col-{col + 1} row-{row+1}."))
                    self.print_grid()

                    if all(self.grid[row][col] != 0 for row in range(9) for col in range(9)):
                        solved = True
                        return solved

                elif not self.is_valid(self.grid, row, col, num):
                    self.grid[row][col] = temp_value
                    if self.tries > 1:
                        print(red(f"Invalid move! {num} can't go in col-{col + 1} row-{row + 1} (conflicts with existing numbers).\n"))
                        self.tries -= 1
                        continue
                    else:
                        print(red(f"You have exceeded 3 tries! Game Over! ❌\n"))
                        return solved
    
    def evaluate(self, answer):
        """Convert the raw summary into a result outcome string."""
        if (answer):
            outcome = "Win"
        else:
            outcome = "Lose"
        return {"outcome": outcome}

    def reward(self, result):
        """Translate outcome into currency and pet happiness and display a summary."""
        outcome = result.get("outcome")
        if outcome == "Win":
            pet_happiness = 15
            print("\nYou solved the sudoku! 🎉")
        else:
            self.coins -= 50
            pet_happiness = 0
            print("\nYou failed to solve the sudoku.. 😾")
        
        print(f"Reward: Rp. {'{:,}'.format(self.coins * 1000)}. Pet happiness (+{pet_happiness})")
        print(green(f"You received Rp. {'{:,}'.format(self.coins * 1000)} 🎉"))
        return {"currency": self.coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        """Run an entire Sudoku game and return rewards."""
        self.setup(player, pet)
        self.display_menu()
        self.build_question()
        summary = self.build_game()
        result = self.evaluate(summary)
        reward = self.reward(result)
        return reward

class MinigameEngine:
    """Registry for minigame strategies and helper to play them by name."""

    def __init__(self):
        self._games = {}

    def register(self, game: MinigameStrategy) -> None:
        self._games[game.name] = game

    def list_games(self) -> List:
        return list(self._games.keys())

    def play(self, name, player, pet):
        game = self._games.get(name)
        if not game:
            print("This minigame currently not available!")
            return {"currency": 0, "pet_happiness": 0}
        return game.play(player, pet)

def engine() -> MinigameEngine:
    """Convenience factory to build an engine pre-registered with available minigames."""
    engine = MinigameEngine()
    engine.register(MathQuiz())
    engine.register(TicTacToe())
    engine.register(MemoryMatch())
    engine.register(BattleContest())
    engine.register(Sudoku())
    return engine
from __future__ import annotations
from typing import Any, Dict, List
from .formatter import GARIS
from abc import ABC, abstractmethod
from random import randint, choice, random
import time
import operator
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

class MinigameStrategy(ABC):
    name: str

    @abstractmethod
    def setup(self, player: Any, pet: Any) -> None:
        pass

    @abstractmethod
    def display_menu(self) -> None:
        pass

    @abstractmethod
    def get_input(self) -> Any:
        pass

    @abstractmethod
    def build_question(self) -> Any:
        pass

    @abstractmethod
    def build_game(self) -> Any:
        pass

    @abstractmethod
    def evaluate(self, answer: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def reward(self, result: Dict[str, Any]) -> Dict[str, int]:
        pass
    
    @abstractmethod
    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        pass

class MathQuiz(MinigameStrategy):
    name = "Math Quiz"

    OPS = {
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
        print("\n" + GARIS)
        print("➕ Math Quiz ➗")
        print(GARIS)
        print("🔍 This game is created to test your logical thinking skill! 🔍")
        print("🧠 Answer the given arithmetic questions as fast and accurately as you can... 🤓")
        print("You will get your coin rewards and boost your pet's happiness! 😸")
        print(GARIS)
        print("Before we start, please choose your difficulty: ")
        print(GARIS)
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Master")
        print(GARIS)
        print("NOTE: Any user's input other than 1-4 will be considered 1 (Default: Difficulty Easy)")
        print(GARIS)
    
    def get_input(self):
        diff = int(input("Choose your difficulty (1-4): ").strip())
        if (diff not in range(1, 5)):
            diff = 1
        self.difficulty = diff
    
    def build_question(self):
        if (self.difficulty == 1):
            q_num = 5
            _max = 10
            ops = ["+", "-"]
        elif (self.difficulty == 2):
            q_num = 10
            _max = 30
            ops = ["+", "-", "*", "/"]
        elif (self.difficulty == 3):
            q_num = 20
            _max = 50
            ops = ["+", "-", "*", "/", "**"]
        elif (self.difficulty == 4):
            q_num = 20
            _max = 60
            ops = ["+", "-", "*", "/", "%", "**"]
        
        for _ in range(q_num):
            a = randint(1, _max)
            b = randint(1, _max)
            op = choice(ops)
            if (op == "/"):
                b = randint(1, _max // randint(1, _max - 1))
                a = b * randint(1, max(1, _max // max(1, b)))
            elif (op == "**"):
                b = randint(1, _max // 10)
            self.questions.append((a, op, b))

    def build_game(self):
        print(f"\nYou will be asked {len(self.questions)} questions. Type your answer (must be an int): ")
        print(GARIS)
        self.start_time = time.time()
        user_answers = []
        for i, (a, op, b) in enumerate(self.questions, start=1):
            ans = int(input(f"Q{i}: {a} {op} {b} = ").strip())
            user_answers.append(ans)
        self.end_time = time.time()
        return user_answers

    def evaluate(self, user_answers):
        for (a, op, b), u in zip(self.questions, user_answers):
            func = self.OPS.get(op)
            if (func):
                expected = func(a, b)
            else:
                expected = None
            self.answers.append(expected)
            if (expected and u == expected):
                self.correct += 1
        elapsed = max(0.001, self.end_time - self.start_time) if self.start_time and self.end_time else 0.0
        accuracy = self.correct / len(self.questions)
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
        correct = result.get("correct", 0)
        total = result.get("total", 1)
        diff = self.difficulty if hasattr(self, "difficulty") else 1
        time_penalty = int(result["elapsed"] // 5)
        coins = max(0, correct * 5 * diff - time_penalty)
        pet_happiness = correct

        print(f"\nResult: {correct}/{total} correct in {result["elapsed"]:.2f}s (accuracy {round(result["accuracy"] * 100)}%)")
        print(f"You earned Rp. Rp. {'{:,}'.format(coins * 1000)} and your pet gains {pet_happiness} happiness.")
        return {"currency": coins, "pet_happiness": pet_happiness}
    
    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        self.setup(player, pet)
        self.display_menu()
        self.get_input()
        self.build_question()
        answer = self.build_game()
        result = self.evaluate(answer)
        reward = self.reward(result)
        return reward

class TicTacToe(MinigameStrategy):
    name = "Tic Tac Toe"

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.board: List[List[str]] = [" "] * 9
        self.player_mark = "X"
        self.pet_mark = "O"
        self.first = True
        self.winner = None

    def display_menu(self):
        print("\n" + GARIS)
        print("⭕ Tic Tac Toe ✖️")
        print(GARIS)
        print("Let's play classic 3x3 Tic-Tac-Toe with your pet!")
        print("You are X, your pet is O. Place number between 1-9 (top-left: 1, top-right: 9).")
        print(GARIS)
        print("Win ---> more coins")
        print("Draw ---> small coins")
        print("Loss ---> no coins.")
        print(GARIS)
    
    def build_question(self):
        return None
    
    def render_board(self):
        b = self.board
        print()
        print(f" {b[0]} | {b[1]} | {b[2]} ")
        print("---+---+---")
        print(f" {b[3]} | {b[4]} | {b[5]} ")
        print("---+---+---")
        print(f" {b[6]} | {b[7]} | {b[8]} ")
        print()

    def available_moves(self):
        return [i for i, v in enumerate(self.board) if v == " "]
    
    def get_input(self):
        while True:
            choice = input("Do you want to play first (Y/N)? ").strip().lower()
            if (choice == "y"):
                self.first = True
                break
            elif (choice == "n"):
                self.first = False
                break
            print("Please answer Y/N!")
    
    def check_winner(self):
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # horizontal
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # vertical
            (0, 4, 8), (2, 4, 6) # Diagonal
        ]

        for a, b, c in lines:
            if (self.board[a] != " ") and (self.board[a] == self.board[b] == self.board[c]):
                return self.board[a]
        if all(cell != " " for cell in self.board):
            return "D"
        return None
            
    def make_move(self, index, mark):
        if (0 <= index < 9) and (self.board[index] == " "):
            self.board[index] = mark
            return True
        return False
    
    def winning_move(self, mark: str):
        for move in self.available_moves():
            self.board[move] = mark
            winner = self.check_winner()
            self.board[move] = " "
            if (winner == mark):
                return move
        return None
    
    def pet_move(self):
        move = self.winning_move(self.pet_mark)
        if (move):
            return move
        move = self.winning_move(self.player_mark)
        if (move):
            return move 
        corners = [i for i in [0, 2, 6, 8] if i in self.available_moves()]
        if (corners):
            return choice(corners)
        return choice(self.available_moves())
    
    def player_move(self):
        print("\n" + GARIS)
        print("It's your turn! Pick your cell now!")
        print(GARIS)
        try:
            idx = int(input("\nChoose cell (1-9): ").strip()) - 1
        except ValueError:
            print("Please input number!")
        else:
            if (idx < 0 or idx > 8):
                print("Cell number cannot be less than 1 or more than 9!")
                return None
            else:
                if (idx in self.available_moves()):
                    return idx
                else:
                    print("Cell has been placed with mark!")
                    return None
    
    def build_game(self):
        self.board = [" "] * 9
        player_turn = self.first
        self.render_board()
        while True:
            if player_turn:
                move = None
                while (move is None):
                    move = self.player_move()
                self.make_move(move, self.player_mark)
            else:
                move = self.pet_move()
                self.make_move(move, self.pet_mark)
                print(f"Pet placed O at at {move + 1}.")
            self.render_board()
            winner = self.check_winner()
            if (winner):
                self.winner = winner
                break
            player_turn = not player_turn
        
        return {"winner": self.winner}
    
    def evaluate(self, summary):
        winner = self.winner
        if winner == self.player_mark:
            outcome = "Win"
        elif winner == self.pet_mark:
            outcome = "Lose"
        else:
            outcome = "Draw"
        return {"outcome": outcome}

    def reward(self, result):
        outcome = result.get("outcome")
        if (outcome == "Win"):
            coins = 20
            pet_happiness = 0
            print("You win! 🎉")
        elif (outcome == "Draw"):
            coins = 5
            pet_happiness = 2
            print("It's a draw!")
        else:
            coins = 0
            pet_happiness = 5
            print("You lose.. 🥲")
        print("Your pet is having fun playing with you!")
        print(f"Reward: {coins} coins, pet happiness (+{pet_happiness})")
        return {"currency": coins, "pet_happiness": pet_happiness}
    
    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        self.setup(player, pet)
        self.display_menu()
        self.get_input()
        self.build_question()
        summary = self.build_game()
        result = self.evaluate(summary)
        reward = self.reward(result)
        return reward

class MemoryMatch(MinigameStrategy):
    name = "Memory Match"

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
    
    def display_menu(self):
        print("\n" + GARIS)
        print("🧩 Memory Match 🧩")
        print(GARIS)
        print("Memorize a short sequence, then reproduce it.")
        print("Faster and more accurate answers give better rewards.")
        print(GARIS)
        print("Choose difficulty:")
        print(GARIS)
        print("1. Easy   (sequence length 3-4, words)")
        print("2. Medium (sequence length 5-6, digits)")
        print("3. Hard   (sequence length 6-8, mixed digits/words)")
        print(GARIS)
    
    def get_input(self):
        diff = int(input("Choose difficulty (1-3): ").strip())
        if diff not in range(1, 4):
            diff = 1
        self.difficulty = diff
    
    def build_question(self):
        diff = self.difficulty
        if (diff == 1):
            self.length = choice([3, 4])
            self.charset = "words"
        elif (diff == 2):
            self.length = choice([5, 6])
            self.charset = "digits"
        else:
            self.length = choice([6, 7, 8])
            self.charset = "mixed"

        words = ["bow", "candle", "candy", "carolers", "carols", "blitzen", "ceremonious", "bauble", "emmanuel", "evergreen"]

        if (self.charset == "digits"):
            self.sequence = [str(randint(0, 9)) for _ in range(self.length)]
        elif (self.charset == "words"):
            for _ in range(self.length):
                self.sequence.append(choice(words))
        else:
            self.sequence = []
            for _ in range(self.length):
                if random() < 0.6:
                    self.sequence.append(str(randint(0, 9)))
                else:
                    self.sequence.append(choice(words))
    
    def build_game(self):
        print("\n" + GARIS)
        print("Game started!")
        print(GARIS)
        print("Memorize this sequence:")
        print(" ".join(self.sequence))
        time.sleep(1.0 + 0.5 * self.length)
        clear()
        print("Now type the sequence separated by spaces (e.g. \"1 2 3\" or \"cat dog 5\" or \"cat dog fruit\").")
        ans = input("Your answer: ").strip()
        ans_list = ans.split()
        return ans_list

    def evaluate(self, answer):
        self.user_response = answer
        correct = 0
        for expected, ans in zip(self.sequence, self.user_response):
            if (expected == ans):
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
        correct = int(result.get("correct", 0))
        total = int(result.get("total", 1))
        exact = bool(result.get("exact", False))
        coins = correct * int(self.difficulty)

        if (exact) and (total > 0):
            coins += (5 * int(self.difficulty))

        pet_happiness = correct // int(self.difficulty)
        
        print(f"Sequence was: {' '.join(result['sequence'])}")
        print(f"Your response: {' '.join(result['response']) if result['response'] else '(none)'}")
        print(f"Correct: {correct}/{total}")
        if (exact):
            print("Perfect! Bonus awarded!")
        print(f"You earned Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})")
        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        self.setup(player, pet)
        self.display_menu()
        self.get_input()
        self.build_question()
        answer = self.build_game()
        result = self.evaluate(answer)
        return self.reward(result)

class MinigameEngine:
    def __init__(self):
        self._games = {}
    
    def register(self, game: MinigameStrategy) -> None:
        self._games[game.name] = game
    
    def list_games(self) -> List:
        return list(self._games.keys())

    def play(self, name, player, pet):
        game = self._games.get(name)
        if (not game):
            print("This minigame currently not available!")
            return {"currency": 0, "pet_happiness": 0}
        return game.play(player, pet)

def engine() -> MinigameEngine:
    engine = MinigameEngine()
    engine.register(MathQuiz())
    engine.register(TicTacToe())
    engine.register(MemoryMatch())
    return engine
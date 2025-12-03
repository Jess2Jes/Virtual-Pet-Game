from __future__ import annotations
from typing import Any, Dict, List, Tuple
from .formatter import GARIS
from abc import ABC, abstractmethod
from random import randint, choice, random
import time
import operator
import os
from .user import User
from colorama import Fore, init

init(autoreset=True)

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
        print(Fore.YELLOW + f"\nYou will be asked {len(self.questions)} questions. Type your answer (must be an int): ")
        print(GARIS)
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
        print(f"You earned Rp. {'{:,}'.format(coins * 1000)} and your pet gains {pet_happiness} happiness.")
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
        print("\n" + GARIS)
        print("⭕ Tic Tac Toe ✖️")
        print(GARIS)
        print("Let's play classic Tic-Tac-Toe with your pet!")
        print("You are X, your pet is O.")
        print(GARIS)
        print("Win ---> more currency")
        print("Draw ---> small currency")
        print("Loss ---> no currency")
        print(GARIS)
    
    def build_question(self):
        print(Fore.YELLOW + "Choose the size of your Tic Tac Toe board!")
        print(GARIS)
        print("1. 3 x 3 board")
        print("2. 4 x 4 board")
        print("3. 5 x 5 board")
        print(GARIS)
        diff = int(input("Choose your size of board (1/2/3): ").strip())
        if (diff not in range(1, 4)):
            diff = 1
        self.difficulty = diff
        if (self.difficulty == 1):
            length = 3
            self.win_length = 3
        elif (self.difficulty == 2):
            length = 4
            self.win_length = 4
        else:
            length = 5
            self.win_length = 3
        
        self.row_length = length
        self.col_length = length
        self.board = [[" " for _ in range(self.col_length)] for _ in range(self.row_length)]
    
    def render_board(self):
        print()
        print("   " + " ".join(f"{c+1:3}" for c in range(self.col_length)))
        print("  +" + "---+" * self.col_length)
        for r in range(self.row_length):
            row_cells = " | ".join(self.board[r][c] if self.board[r][c] != " " else " " for c in range(self.col_length))
            print(f"{r+1:2}| {row_cells} |")
            print("  +" + "---+" * self.col_length)
        print()

    def available_moves(self):
        available: List[Tuple[int, int]] = []
        for i in range(self.row_length):
            for j in range(self.col_length):
                if (self.board[i][j] == " "):
                    available.append((i, j))
        return available
    
    def get_input(self):
        while True:
            choice = input("\nDo you want to play first (Y/N)? ").strip().lower()
            if (choice == "y"):
                self.first = True
                break
            elif (choice == "n"):
                self.first = False
                break
            print(Fore.RED + "Please answer Y/N!")
    
    def check_winner(self):
        counts = {}
        
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
        for col in range(self.row_length):
            for row in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, 0, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_diagonal_wins(self, counts: dict) -> None:
        """Check for diagonal winning sequences (top-left to bottom-right)."""
        for row in range(self.row_length - self. win_length + 1):
            for col in range(self. row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, 1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_anti_diagonal_wins(self, counts: dict) -> None:
        """Check for anti-diagonal winning sequences (top-right to bottom-left)."""
        for row in range(self.row_length - self. win_length + 1):
            for col in range(self. win_length - 1, self.col_length):
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
        if (0 <= row < self.row_length) and (0 <= col < self.col_length) and (self.board[row][col] == " "):
            self.board[row][col] = mark
            return True
        return False
    
    def winning_move(self, mark):
        for row, col in self.available_moves():
            self.board[row][col] = mark
            winner = self.check_winner()
            self.board[row][col] = " "
            if (winner.get(mark, 0) > 0):
                return row, col
        return None
    
    def _center(self):
        return (self.row_length // 2, self.col_length // 2)

    def _corners(self):
        return [
            (0, 0),
            (0, self.col_length - 1),
            (self.row_length - 1, 0),
            (self.row_length - 1, self.col_length - 1),
        ]

    def _first_available(self, positions, available_set):
        for pos in positions:
            if pos in available_set:
                return pos
        return None

    def _edge_positions(self):
        edges = []
        for c in range(1, self.col_length - 1):
            edges.append((0, c))
            edges.append((self.row_length - 1, c))
        for r in range(1, self.row_length - 1):
            edges.append((r, 0))
            edges.append((r, self.col_length - 1))
        return edges

    def pet_move(self):
        available = set(self.available_moves())

        if len(available) == self.row_length * self.col_length:
            center = self._center()
            if center in available:
                return center
            corner = self._first_available(self._corners(), available)
            if corner:
                return corner

        # Win if possible
        win = self.winning_move(self.pet_mark)
        if win:
            return win

        # Block opponent win
        block = self.winning_move(self.player_mark)
        if block:
            return block

        # Create a fork if possible
        fork_move = self.fork_move(self.pet_mark)
        if fork_move:
            return fork_move

        # Block opponent fork
        block_fork = self.fork_move(self.player_mark)
        if block_fork:
            return block_fork

        # Take center if available
        center = self._center()
        if center in available:
            return center

        # Take a corner if available
        corner = self._first_available(self._corners(), available)
        if corner:
            return corner

        # On larger boards prefer the best edge
        if self.row_length >= 4:
            edges = [e for e in self._edge_positions() if e in available]
            if edges:
                best_edge = self.best_edge(edges)
                if best_edge:
                    return best_edge

        # Fallback: random available move
        return choice(list(available))
    
    def fork_move(self, mark):
        best_move = None
        max_forks = 0

        for move in self.available_moves():
            self.board[move[0]][move[1]] = mark

            fork_count = 0
            for test_move in self.available_moves():
                self.board[test_move[0]][test_move[1]] = mark
                wins = self.check_winner()
                
                if (wins.get(mark, 0) > 0):
                    fork_count += 1
                
                self.board[test_move[0]][test_move[1]] = " "
            
            self.board[move[0]][move[1]] = " "
        
            if (fork_count > max_forks):
                max_forks = fork_count
                best_move = move
        
        if (max_forks >= 2):
            return best_move
        
        return None

    def best_edge(self, edges):
        """Select the best edge position based on board size heuristics."""
        if not edges:
            return None

        if self.row_length == 4:
            return self._best_edge_four(edges)

        if self.row_length == 5:
            return self._best_edge_five(edges)

        return edges[0] if edges else None


    def _best_edge_four(self, edges):
        """Evaluate edges for 4x4 board and pick the highest scoring one."""
        best_score = float("-inf")
        best_edge = None

        for edge in edges:
            base = self._base_score_for_edge(edge)
            likely_wins = self._count_likely_wins_if_mark(edge, self.pet_mark)
            score = base + likely_wins * 0.5

            if score > best_score:
                best_score = score
                best_edge = edge

        return best_edge


    def _best_edge_five(self, edges):
        """For 5x5 board, prefer an immediate winning edge, otherwise the edge closest to center."""
        # First: if any edge immediately creates a winning move, take it.
        for edge in edges:
            try:
                self.board[edge[0]][edge[1]] = self.pet_mark
                winning_move = self.winning_move(self.pet_mark)
            finally:
                self.board[edge[0]][edge[1]] = " "

            if winning_move:
                return edge

        # Otherwise: choose the edge with minimal Manhattan distance to center (2,2)
        center_r = (self.row_length - 1) // 2
        center_c = (self.col_length - 1) // 2

        best_edge = None
        best_dist = float("inf")
        for edge in edges:
            dist = abs(edge[0] - center_r) + abs(edge[1] - center_c)
            if dist < best_dist:
                best_dist = dist
                best_edge = edge

        return best_edge


    def _base_score_for_edge(self, edge):
        """Compute base proximity score for an edge position."""
        row_distance = abs(edge[0] - (self.row_length // 2))
        col_distance = abs(edge[1] - (self.col_length // 2))
        return 2 - (row_distance + col_distance)


    def _count_likely_wins_if_mark(self, edge, mark):
        """
        Simulate placing `mark` at `edge`, then count how many next-moves would
        lead to an immediate win for that mark. Board state is restored.
        """
        likely_wins = 0
        try:
            # place the mark at the edge
            self.board[edge[0]][edge[1]] = mark
            # snapshot of available moves after placing the edge
            moves = list(self.available_moves())

            for test_move in moves:
                try:
                    self.board[test_move[0]][test_move[1]] = mark
                    wins = self.check_winner()
                    if wins.get(mark, 0) > 0:
                        likely_wins += 1
                finally:
                    self.board[test_move[0]][test_move[1]] = " "
        finally:
            # restore the edge
            self.board[edge[0]][edge[1]] = " "

        return likely_wins

    def player_move(self):
        print("\n" + GARIS)
        print("It's your turn! Pick your cell now!")
        print(GARIS)
        try:
            row, col = map(int, input(f"\nEnter row (1-{self.row_length}) and column (1-{self.col_length}) --> ex: 2 3: ").strip().split())
            row -= 1
            col -= 1
        except ValueError:
            print(Fore.RED + "Please input two numbers separated by space (e.g. '2 3').")
            return None
        if (row < 0 or row > self.row_length):
            print(Fore.RED + f"Row number cannot be less than 1 or more than {self.row_length}!")
            return None
        if (col < 0 or col > self.col_length):
            print(Fore.RED + f"Column number cannot be less than 1 or more than {self.col_length}!")
            return None
        if ((row, col) not in self.available_moves()):
            print(Fore.YELLOW + "Cell has been placed with mark!")
            return None
        
        return row, col
    
    def count_sequence(self):
        self.render_board()
        counts = self.check_winner()
        player = counts.get(self.player_mark, 0)
        pet = counts.get(self.pet_mark, 0)
        if (player > pet):
            winner = self.player_mark
        elif (pet > player):
            winner = self.pet_mark
        else:
            winner = None
            
        return winner
    
    def build_game(self):
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
        print(f"Pet placed '{self.pet_mark}' at at (row-{row + 1} col-{col + 1}).")

    def _check_game_over(self) -> bool:
        if self.row_length >= 3 or ((self.win_length <= 4) and (self.row_length < 4)):
            if self.check_winner() or not self.available_moves():
                self.render_board()
                self.winner = self.count_sequence()
                return True
        return False

    
    def evaluate(self, summary):
        winner = summary.get("winner")
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
            print("\nYou win! 🎉")
        elif (outcome == "Draw"):
            coins = 5
            pet_happiness = 2
            print("\nIt's a draw!")
        else:
            coins = 0
            pet_happiness = 5
            print("\nYou lose.. 🥲")
        print("Your pet is having fun playing with you!")
        print(f"Reward: Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})")
        return {"currency": coins, "pet_happiness": pet_happiness}
    
    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        self.setup(player, pet)
        self.display_menu()
        self.build_question()
        self.get_input()
        summary = self.build_game()
        result = self.evaluate(summary)
        reward = self.reward(result)
        return reward

class MemoryMatch(MinigameStrategy):
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
        print("\n" + GARIS)
        print("🧩 Memory Match 🧩")
        print(GARIS)
        print("Memorize a short sequence, then reproduce it.")
        print("Faster and more accurate answers give better rewards.")
        print(GARIS)
        print("Choose difficulty:")
        print(GARIS)
        print("1. Easy   (sequence length 5-6, digits)")
        print("2. Medium (sequence length 3-4, words)")
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
            self.length = choice([5, 6])
            self.charset = "digits"
        elif (diff == 2):
            self.length = choice([3, 4])
            self.charset = "words"
        else:
            self.length = choice([6, 7, 8])
            self.charset = "mixed"

        if (self.charset == "digits"):
            self.sequence = [str(randint(0, 9)) for _ in range(self.length)]
        elif (self.charset == "words"):
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
        
        print("\n" + GARIS)
        print("RESULT".center(len(GARIS)))
        print(GARIS)
        print(f"Sequence was: {' '.join(result['sequence'])}")
        print(f"Your response: {' '.join(result['response']) if result['response'] else '(none)'}")
        print(f"\nCorrect: {correct}/{total}")
        if (exact):
            print(Fore.GREEN + "Perfect! Bonus awarded! 🎉")
        print(f"You earned Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})\n")
        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        self.setup(player, pet)
        self.display_menu()
        self.get_input()
        self.build_question()
        answer = self.build_game()
        result = self.evaluate(answer)
        return self.reward(result)

class BattleContest(MinigameStrategy):
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
        if (other_players_with_pets):
            self.opponent = choice(other_players_with_pets)
            self.opponent_pet = choice(self.opponent.pets)
        else:
            print(Fore.RED + "\nOther players currently doesn't have any pets yet!\n")
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
        print("\n" + GARIS)
        print(f"PET BATTLE TOURNAMENT -> ROUND - {self.current_round}".center(len(GARIS)))
        print(GARIS)
        print("\n" + GARIS)
        print(f"Your Pet: {self.player_pet.name}")
        print(f"Health: {self.player_health}")
        print(f"Strength: {self.player_pet_stats['strength']}")
        print(f"Agility: {self.player_pet_stats['agility']}")
        print('-' * len(GARIS))
        
        if (self.opponent_pet):
            print(f"Opponent: {self.opponent_pet.name}")
            print(f"Health: {self.opponent_health}")
            print(f"Strength: {self.player_pet_stats['strength']}")
            print(f"Agility: {self.player_pet_stats['agility']}")
        
        print(GARIS)
        print("\nBattle Options:")
        print(GARIS)
        print("1. Attack 🗡️")
        print("2. Defend 🛡️")
        print("3. Special Move ✨")
        print("4. Heal ❤️‍🩹")
        print(GARIS)
    
    def get_input(self):
        while True:
            try:
                choice = int(input("Choose your action (1-4): "))
                if (1 <= choice <= 4):
                    return choice
                else:
                    print(Fore.RED + "Please enter a number between 1-4!")
            except ValueError:
                print(Fore.RED + "Please enter a valid number!")
    
    def build_question(self) -> Any:
        print("\n" + GARIS)
        print("Battle Starting!")
        print(GARIS)
        print(f"{self.player_pet.name} VS {self.opponent_pet.name}")
        print("Prepare for battle!")
        time.sleep(2)

    def build_game(self) -> Any:
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
        """Execute the opponent's action."""
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
        """Player defends."""
        defense_bonus = randint(2, 5) * 300
        print(f"\n{self.player_pet.name} defends 🛡️!")
        print(f"Damage reduction: {defense_bonus}")

    def _player_special_move(self) -> None:
        """Player uses special move (only on even rounds)."""
        if (self.current_round % 2 == 0):
            special_damage = (randint(10, 15) + self.player_pet_stats["strength"] // 2) * 600
            self.opponent_health -= special_damage
            print(f"\n{self.player_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            print(Fore.RED + "\nSpecial moves are locked in odd rounds!")

    def _player_heal(self) -> None:
        """Player heals."""
        if (self.player_heal_count < self.player_heal_limit):
            heal_amount = randint(8, 12) * 500
            self.player_health += heal_amount
            print(f"\n{self.player_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.player_heal_count += 1
        else:
            print(Fore.RED + "\nYou already healed 3 times!")

    def _opponent_attack(self) -> None:
        """Opponent attacks the player."""
        damage = (randint(4, 8) + self.opponent_pet_stats["strength"] // 3) * 300
        self.player_health -= damage
        print(f"{self.opponent_pet.name} attacks for {damage} damage ⚔️!")

    def _opponent_defend(self) -> None:
        """Opponent defends."""
        defense_bonus = randint(1, 4) * 300
        print(f"{self.opponent_pet. name} defends 🛡️!")
        print(f"Damage reduction: {defense_bonus}")

    def _opponent_special_move(self) -> None:
        """Opponent uses special move (only on odd rounds)."""
        if (self.current_round % 2 != 0):
            special_damage = (randint(8, 12) + self.opponent_pet_stats["strength"] // 2) * 600
            self.player_health -= special_damage
            print(f"{self.opponent_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            print(Fore. RED + "\nOpponent's special moves are restricted on even rounds!")

    def _opponent_heal(self) -> None:
        """Opponent heals."""
        if (self.opponent_heal_count < self.opponent_heal_limit):
            heal_amount = randint(6, 10) * 500
            self.opponent_health += heal_amount
            print(f"{self.opponent_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.opponent_heal_count += 1
        else:
            print(Fore. RED + "\nOpponent's healing ability are restricted to 5 times only!")

    def _determine_battle_outcome(self) -> None:
        """Determine and display the battle outcome."""
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
        victory = bool(result.get("victory", False))
        performance_score = int(result.get("performance_score", 0))
        player_health_remaining = int(result.get("player_health_remaining", 0))
        
        coins = 0
        pet_happiness = 0
        
        if (victory):
            coins = 20 + (performance_score // 10)
            pet_happiness = 15 + (player_health_remaining // 5)
            print(Fore.GREEN + f"🎉 VICTORY! {self.player_pet.name} won the battle!")
        else:
            coins = 5 + (performance_score // 20)
            pet_happiness = 5 + (player_health_remaining // 10)
            print(Fore.RED + f"💔 Defeat... {self.player_pet.name} was defeated.")
        
        print("\n" + GARIS)
        print("BATTLE RESULTS")
        print(GARIS)
        print(f"Performance Score: {performance_score}/100")
        print(f"Health Remaining: {player_health_remaining}")
        print(f"Coins Earned: {'{:,}'.format(coins * 1000)}")
        print(f"Pet Happiness: (+{pet_happiness})")
        print(GARIS)
        
        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        res = self.setup(player, pet)
        if (res):
            self.build_question()
            battle_result = self.build_game()
            evaluation = self.evaluate(battle_result)
            return self.reward(evaluation)
    
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
    engine.register(BattleContest())
    return engine
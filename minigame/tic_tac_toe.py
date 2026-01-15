"""Tic Tac Toe minigame implementation (conforms to MinigameStrategy interfaces)."""

from random import choice
from typing import Any, Dict, List, Tuple
from .base_class import MinigameStrategy
from utils.ports import ConsoleIO, InputPort, OutputPort
from utils.colorize import red, green, yellow
from constants.configs import UIConfig as UIC

class TicTacToe(MinigameStrategy):
    """n x n Tic-Tac-Toe with your pet and configurable board sizes."""

    name = "Tic Tac Toe"

    def __init__(self, io: InputPort | OutputPort | None = None):
        self.io: InputPort | OutputPort = io or ConsoleIO()

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
        self.io.write("\n" + UIC.LINE)
        self.io.write("⭕ Tic Tac Toe ✖️")
        self.io.write(UIC.LINE)
        self.io.write("Let's play classic Tic-Tac-Toe with your pet!")
        self.io.write("You are X, your pet is O.")
        self.io.write(UIC.LINE)
        self.io.write("Win ---> more currency")
        self.io.write("Draw ---> small currency")
        self.io.write("Loss ---> no currency")
        self.io.write(UIC.LINE)

    def get_input(self):
        """Ask if the player wants to play first (Y/N)."""
        while True:
            choice_val = self.io.read("\nDo you want to play first (Y/N)? ").strip().lower()
            if choice_val == "y":
                self.first = True
                break
            if choice_val == "n":
                self.first = False
                break
            self.io.write(red("Please answer Y/N!"))

    def build_question(self):
        """Collect board-size choice and prepare an empty board."""
        self.io.write(yellow("Choose the size of your Tic Tac Toe board!"))
        self.io.write(UIC.LINE)
        self.io.write("1. 3 x 3 board")
        self.io.write("2. 4 x 4 board")
        self.io.write("3. 5 x 5 board")
        self.io.write(UIC.LINE)
        try:
            diff = int(self.io.read("Choose your size of board (1/2/3): ").strip())
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
        lines = []
        lines.append("")
        lines.append("   " + " ".join(f"{c+1:3}" for c in range(self.col_length)))
        lines.append("  +" + "---+" * self.col_length)
        for r in range(self.row_length):
            row_cells = " | ".join(self.board[r][c] if self.board[r][c] != " " else " " for c in range(self.col_length))
            lines.append(f"{r+1:2}| {row_cells} |")
            lines.append("  +" + "---+" * self.col_length)
        lines.append("")
        self.io.write("\n".join(lines))

    def available_moves(self):
        """Return list of empty cells as (row, col) tuples."""
        available: List[Tuple[int, int]] = []
        for i in range(self.row_length):
            for j in range(self.col_length):
                if self.board[i][j] == " ":
                    available.append((i, j))
        return available

    def check_winner(self):
        """Check the board for winning sequences in all directions and return counts per mark."""
        counts = {}
        self._check_horizontal_wins(counts)
        self._check_vertical_wins(counts)
        self._check_diagonal_wins(counts)
        self._check_anti_diagonal_wins(counts)
        return counts

    def _check_horizontal_wins(self, counts: dict) -> None:
        for row in range(self.row_length):
            for col in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 0, 1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_vertical_wins(self, counts: dict) -> None:
        for col in range(self.col_length):
            for row in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, 0, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_diagonal_wins(self, counts: dict) -> None:
        for row in range(self.row_length - self.win_length + 1):
            for col in range(self.row_length - self.win_length + 1):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, 1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _check_anti_diagonal_wins(self, counts: dict) -> None:
        for row in range(self.row_length - self.win_length + 1):
            for col in range(self.win_length - 1, self.col_length):
                first = self.board[row][col]
                if self._is_winning_sequence(row, col, 1, -1, first):
                    counts[first] = counts.get(first, 0) + 1

    def _is_winning_sequence(self, start_row: int, start_col: int,
                             row_delta: int, col_delta: int, mark: str) -> bool:
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
        """Compute the pet's move using heuristics."""
        for mark in [self.pet_mark, self.player_mark]:
            move = self.winning_move(mark)
            if move:
                return move

        for mark in [self.pet_mark, self.player_mark]:
            move = self.fork_move(mark)
            if move:
                return move

        move = self._choose_center()
        if move:
            return move

        move = self._choose_corner()
        if move:
            return move

        move = self._choose_edge() if self.row_length >= 4 else None
        if move:
            return move

        return choice(self.available_moves())

    def _choose_center(self):
        """Return the center cell if available, else None."""
        center = (self.row_length // 2, self.col_length // 2)
        return center if center in self.available_moves() else None

    def _choose_corner(self):
        """Return the first available corner, else None."""
        corners = [
            (0, 0),
            (0, self.col_length - 1),
            (self.row_length - 1, 0),
            (self.row_length - 1, self.col_length - 1)
        ]
        for corner in corners:
            if corner in self.available_moves():
                return corner
        return None

    def _choose_edge(self):
        """Return the best edge cell if available, else None."""
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

        return self.best_edge(edges) if edges else None

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
        """Select the best edge cell from a list using heuristics based on board size."""
        if not edges:
            return None

        if self.row_length == 4:
            return self._best_edge_4(edges)
        if self.row_length == 5:
            return self._best_edge_5(edges)

        return edges[0]

    def _best_edge_4(self, edges):
        """Edge selection logic for 4x4 board."""
        best_score = -1
        best_edge = None

        for edge in edges:
            score = self._edge_score_4(edge)
            if score > best_score:
                best_score = score
                best_edge = edge

        return best_edge

    def _edge_score_4(self, edge):
        """Compute a heuristic score for a single edge in 4x4 board."""
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
        return score + likely_wins * 0.5

    def _best_edge_5(self, edges):
        """Edge selection logic for 5x5 board."""
        center = 2
        best_edge = None
        min_distance = float('inf')

        for edge in edges:
            self.board[edge[0]][edge[1]] = self.pet_mark
            if self.winning_move(self.pet_mark):
                self.board[edge[0]][edge[1]] = " "
                return edge
            self.board[edge[0]][edge[1]] = " "

            distance = abs(edge[0] - center) + abs(edge[1] - center)
            if distance < min_distance:
                min_distance = distance
                best_edge = edge

        return best_edge

    def player_move(self):
        """Prompt the player for a row/column move and validate it."""
        self.io.write("\n" + UIC.LINE)
        self.io.write("It's your turn! Pick your cell now!")
        self.io.write(UIC.LINE)
        try:
            row, col = map(int, self.io.read(f"\nEnter row (1-{self.row_length}) and column (1-{self.col_length}) --> ex: 2 3: ").strip().split())
            row -= 1
            col -= 1
        except ValueError:
            self.io.write(red("Please input two numbers separated by space (e.g. '2 3')."))
            return None
        if row < 0 or row >= self.row_length:
            self.io.write(red(f"Row number cannot be less than 1 or more than {self.row_length}!"))
            return None
        if col < 0 or col >= self.col_length:
            self.io.write(red(f"Column number cannot be less than 1 or more than {self.col_length}!"))
            return None
        if (row, col) not in self.available_moves():
            self.io.write(yellow("Cell has been placed with mark!"))
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
        self.io.write(f"Pet placed '{self.pet_mark}' at (row-{row + 1} col-{col + 1}).")

    def _check_game_over(self) -> bool:
        """Check if the game has ended and set the winner."""
        if (self.win_length <= 4) and (self.row_length < 4):
            if self.check_winner():
                self.render_board()
                self.winner = self.count_sequence()
                return True

        if self.row_length >= 3 and (not self.available_moves()):
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
            self.io.write("\nYou win! 🎉")
        elif outcome == "Draw":
            coins = 5
            pet_happiness = 2
            self.io.write("\nIt's a draw!")
        else:
            coins = 0
            pet_happiness = 5
            self.io.write("\nYou lose.. 🥲")
        self.io.write("Your pet is having fun playing with you!")
        self.io.write(f"Reward: Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})")
        self.io.write(green(f"You received Rp. {'{:,}'.format(coins * 1000)} 🎉"))
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
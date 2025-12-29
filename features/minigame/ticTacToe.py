from .baseClass import MinigameStrategy
from typing import Any, Dict, List, Tuple
from random import choice
from utils.colorize import red, green, yellow
from constants.configs import LINE
from colorama import init

init(autoreset=True)

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


from random import shuffle, choice
from .baseClass import MinigameStrategy
import time
from constants.configs import LINE, GRID_LINE
from utils.colorize import red, green, blue, yellow
from colorama import init

init(autoreset=True)

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
        self.start_time = None
        self.end_time = None
    
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
        print(f"  {GRID_LINE}")
        for i, row in enumerate(self.grid):
            if i > 0 and i % 3 == 0:
                print(f"  {GRID_LINE}")
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
        print(f"  {GRID_LINE}")
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

    def _find_empty(self, board):
        """Return the row and column of the first empty cell (0), or (None, None) if the board is full."""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return row, col
        return None, None


    def _shuffled_numbers(self):
        """Return numbers 1–9 in random order for randomized backtracking."""
        numbers = list(range(1, 10))
        shuffle(numbers)
        return numbers


    def _try_number(self, board, row, col, num):
        """Try placing a number in a cell and recursively solve the board.
        
        Returns True if the placement leads to a valid solution, otherwise False.
        """
        if not self.is_valid(board, row, col, num):
            return False

        board[row][col] = num
        if self.solve_sudoku(board):
            return True

        board[row][col] = 0
        return False

    def solve_sudoku(self, board):
        """Solve the Sudoku puzzle using backtracking."""
        row, col = self._find_empty(board)
        if row is None:
            return True

        for num in self._shuffled_numbers():
            if self._try_number(board, row, col, num):
                return True

        board[row][col] = 0
        return False


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
        """Get and validate user input for Sudoku moves."""
        while True:
            choice = input("Enter Move: ").strip().lower()

            command = self._parse_exit_or_hint(choice)
            if command:
                return command

            command = self._parse_clear(choice)
            if command:
                return command

            command = self._parse_move(choice)
            if command:
                return command

            print(red("Invalid input. Please try again.\n"))

    def _parse_exit_or_hint(self, choice):
        """Check if input is an exit or hint command."""
        if choice in ['exit', 'quit', 'q', 'ex', 'e']:
            return 'exit', None
        if choice == 'hint':
            return 'hint', None
        return None

    def _parse_clear(self, choice):
        """Parse 'clear' command and validate position."""
        if not choice.startswith('clear '):
            return None

        parts = choice.split()
        if len(parts) != 2:
            print(red("Invalid clear command. Use format: 'clear 11'.\n"))
            return None

        position = parts[1]
        if len(position) != 2 or not position.isdigit():
            print(red("Invalid clear command. Use format: 'clear 11'.\n"))
            return None

        row, col = int(position[0]) - 1, int(position[1]) - 1
        if self.pre_filled[row][col]:
            print(red('Cannot clear a pre-filled cell!\n'))
            return None

        return 'clear', (row, col)

    def _parse_move(self, choice):
        """Parse a move input and validate it."""
        parts = choice.replace(',', '').split()
        if len(parts) != 2:
            print(red('Invalid input. Use format: 11 5 (col)(row) (value)\n'))
            return None

        position, number_str = parts
        if len(position) != 2 or not position.isdigit():
            print(red("Invalid position. Use format like 11, 23, etc.\n"))
            return None

        try:
            number = int(number_str)
            if number < 1 or number > 9:
                print(red('Number must be between 1 and 9.\n'))
                return None
        except ValueError:
            print(red('Invalid number. Please enter a number between 1 and 9.\n'))
            return None

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
    
    def _handle_hint_action(self):
        hint = self.get_hint()
        print(blue(f"\n 💡 Hint: {hint}\n"))
        return True

    def _handle_exit_action(self):
        print(yellow("\nYou exited."))
        return False

    def _handle_clear_action(self, data):
        """Handle clearing a cell."""
        row, col = data

        if self.grid[row][col] != 0:
            self.grid[row][col] = 0
            print(green(f"\nCleared col-{col + 1} row-{row + 1}."))
            self.print_grid()
        else:
            print(red("Cell is already empty!\n"))

        return True
    
    def _handle_move_action(self, data):
        """Handle placing a number. Returns True if game won, False if lost, None to continue."""
        row, col, num = data
        if self.pre_filled[row][col]:
            print(red(f"Cell {col + 1}{row + 1} is pre-filled with {self.grid[row][col]}. Try a different cell.\n"))
            return True, False

        temp_value = self.grid[row][col]
        self.grid[row][col] = 0

        if self.is_valid(self.grid, row, col, num):
            return self._handle_valid_move(row, col, num)

        elif not self.is_valid(self.grid, row, col, num):
            return self._handle_invalid_move(row, col, num, temp_value)

    def _handle_valid_move(self, row, col, num):
        """Handle a valid move placement."""
        self.grid[row][col] = num
        print(green(f"\nPlaced {num} at col-{col + 1} row-{row+1}."))
        self.print_grid()

        if all(self.grid[row][col] != 0 for row in range(9) for col in range(9)):
            self.end_time = time.time()
            return False, True
        
        return True, False

    def _handle_invalid_move(self, row, col, num, temp_value):
        """Handle an invalid move (reduces tries)."""
        self.grid[row][col] = temp_value
        if self.tries > 1:
            print(red(f"Invalid move! {num} can't go in col-{col + 1} row-{row + 1} (conflicts with existing numbers).\n"))
            self.tries -= 1
            return True, False
        else:
            print(red("You have exceeded 3 tries! Game Over! ❌\n"))
            self.end_time = time.time()
            return False, False
    
    def build_game(self):
        """Main game loop."""

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
        self.start_time = time.time()

        while True:
            print(yellow(f"Tries remaining: ({self.tries}/3)"))
            action, data = self.get_input()
            handler = {
                'exit': self._handle_exit_action,
                'hint': self._handle_hint_action,
                'clear': self._handle_clear_action,
                'move': self._handle_move_action,
            }.get(action)
        
            if handler is None:
                print(red("Invalid action!"))
                continue
            
            if action == 'move':
                should_continue, won = handler(data)
            else:
                should_continue = handler() if data is None else handler(data)
                won = False  
            
            if not should_continue:
                return won
    
    def evaluate(self, answer):
        """Convert the raw summary into a result outcome string."""
        if (answer):
            outcome = "Win"
        else:
            outcome = "Lose"

        elapsed = max(0.001, self.end_time - self.start_time) if self.start_time and self.end_time else 0.0

        return {"outcome": outcome, "elapsed": elapsed}

    def reward(self, result):
        """Translate outcome into currency and pet happiness and display a summary."""
        outcome = result.get("outcome")
        elapsed = result.get("elapsed")
        if outcome == "Win":
            pet_happiness = 15
            print("\nYou solved the sudoku! 🎉")
        else:
            self.coins -= 50
            pet_happiness = 0
            print("\nYou failed to solve the sudoku.. 😾")
        
        print(f"Elapsed time: {elapsed:.2f}s")
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
 
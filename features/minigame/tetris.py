from .baseClass import MinigameStrategy
from typing import Dict
import curses
import time
from random import choice
import logging
from utils.colorize import green, yellow
from constants.configs import LINE
from colorama import init

init(autoreset=True)

class Tetris(MinigameStrategy):
    """A simple tetris minigame where logic-based rewards are determined."""

    name = "Tetris"

    SHAPES = [
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[0, 1, 0], [1, 1, 1]],
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [1, 1, 1]]
    ]   

    WIDTH = 10
    HEIGHT = 20

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.board = [[0] * Tetris.WIDTH for _ in range(Tetris.HEIGHT)]
        self.current_piece = choice(Tetris.SHAPES)
        self.next_piece = choice(Tetris.SHAPES)
        self.piece_offset = [0, Tetris.WIDTH // 2 - len(self.current_piece[0]) // 2]
        self.score = 0
        self.speed = 0.8
        self.next_drop = time.time() + self.speed
        self.stdscr = None
        self.game_over = False
        self.lines_cleared = 0
        self.difficulty = 1
    
    @staticmethod
    def rotate(shape):
        """Rotate a shape 90 degrees clockwise."""
        return [list(row) for row in zip(*shape[::-1])]
    
    def check_collision(self, shape, offset):
        """Check if a shape collides with the board or boundaries."""
        off_y, off_x = offset
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                by = y + off_y
                bx = x + off_x
                if cell and (bx < 0 or bx >= Tetris.WIDTH or by >= Tetris.HEIGHT or (by >= 0 and self.board[by][bx])):
                    return True
        return False

    def merge(self):
        """Merge the current piece into the board."""
        off_y, off_x = self.piece_offset 
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                by = y + off_y
                bx = x + off_x
                if cell and 0 <= by < Tetris.HEIGHT and 0 <= bx < Tetris.WIDTH:
                    self.board[by][bx] = 1
    
    def remove_full_lines(self):
        """Remove completed lines and return number cleared."""
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = Tetris.HEIGHT - len(new_board)
        new_board = [[0] * Tetris.WIDTH for _ in range(lines_cleared)] + new_board
        self.board = new_board
        return lines_cleared

    @staticmethod
    def display_menu():
        """Show a description and choices to the player."""
        print("\n" + LINE)
        print("🟨 Tetris ⬜")
        print(LINE)
        print("Play this classic block-stacking game with your pet!")
        print("\nControls:")
        print("← → : Move left/right")
        print("↑   : Rotate piece")
        print("↓   : Soft drop")
        print("Q   : Quit game")
        print("\nObjective:")
        print("- Clear lines by filling horizontal rows")
        print("- Each line cleared gives 100 points")
        print("- Game gets faster as you clear more lines")
        print("- Game ends when blocks stack to the top")
        print(LINE)
    
    def get_input(self):
        """Collect any initial input from the player."""
        choice = input(yellow("\nPress Enter to start the game...")).strip().lower()
        return choice
    
    def draw_board(self, win):
        """Draw the game board, current piece, and score."""
        win.clear()
        height, width = win.getmaxyx()

        grid_x = max(2, (width - Tetris.WIDTH * 2) // 2)
        grid_y = max(1, (height - Tetris.HEIGHT) // 2)

        self._draw_frame(win, grid_x, grid_y)
        self._draw_board_cells(win, grid_x, grid_y)
        self._draw_piece(win, self.current_piece, self.piece_offset, grid_x, grid_y)
        self._draw_ui(win, grid_x, grid_y)

        win.refresh()


    def _draw_frame(self, win, grid_x, grid_y):
        """Draw the board frame (borders)."""
        for y in range(Tetris.HEIGHT + 2):
            for x in range(Tetris.WIDTH * 2 + 2):
                char = " "
                if y == 0 or y == Tetris.HEIGHT + 1:
                    char = "-"
                elif x == 0 or x == Tetris.WIDTH * 2 + 1:
                    char = "|"
                win.addstr(grid_y + y, grid_x + x, char)


    def _draw_board_cells(self, win, grid_x, grid_y):
        """Draw the placed blocks on the board."""
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    win.addstr(grid_y + 1 + y, grid_x + 1 + x * 2, '[]')


    def _draw_piece(self, win, piece, offset, grid_x, grid_y):
        """Draw a piece at a given offset."""
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                by = y + offset[0]
                bx = x + offset[1]
                if cell and 0 <= by < Tetris.HEIGHT and 0 <= bx < Tetris.WIDTH:
                    win.addstr(grid_y + 1 + by, grid_x + 1 + bx * 2, '[]')


    def _draw_ui(self, win, grid_x, grid_y):
        """Draw score and next piece preview."""
        win.addstr(grid_y, grid_x + Tetris.WIDTH * 2 + 4, f"Score: {self.score}")
        win.addstr(grid_y + 2, grid_x + Tetris.WIDTH * 2 + 4, "Next:")
        for y, row in enumerate(self.next_piece):
            for x, cell in enumerate(row):
                if cell:
                    win.addstr(grid_y + 3 + y, grid_x + Tetris.WIDTH * 2 + 4 + x * 2, "[]")

    
    def build_question(self):
        """Collect difficulty choice before starting the game."""

        print("\nSelect Difficulty Level:")
        print("1. Easy (Slow speed)")
        print("2. Medium (Normal speed)")
        print("3. Hard (Fast speed)")
        print("4. Expert (Very fast)")
        print(LINE)
        try:
            diff = int(input("Choose your difficulty (1/2/3/4): ").strip())
        except ValueError:
            diff = 1
        if diff not in range(1, 5):
            diff = 1
        self.difficulty = diff
        if self.difficulty == 1:
            self.speed = 0.8
        elif self.difficulty == 2:
            self.speed = 0.5
        elif self.difficulty == 3:
            self.speed = 0.3
        else:
            self.speed = 0.15
    
    def handle_input(self, key):
        """Handle keyboard input."""
        if key in [ord('q'), ord('Q')]:
            return 'quit'

        if key == curses.KEY_LEFT:
            self._try_move(0, -1)
        elif key == curses.KEY_RIGHT:
            self._try_move(0, 1)
        elif key == curses.KEY_UP:
            self._try_rotate()
        elif key == curses.KEY_DOWN:
            self._try_drop()

        return 'continue'


    def _try_move(self, d_row, d_col):
        """Attempt to move the piece by (d_row, d_col) if no collision."""
        new_offset = [self.piece_offset[0] + d_row, self.piece_offset[1] + d_col]
        if not self.check_collision(self.current_piece, new_offset):
            self.piece_offset = new_offset


    def _try_rotate(self):
        """Attempt to rotate the current piece if no collision."""
        rotated = self.rotate(self.current_piece)
        if not self.check_collision(rotated, self.piece_offset):
            self.current_piece = rotated


    def _try_drop(self):
        """Attempt to move the piece down; if blocked, merge and spawn next piece."""
        new_offset = [self.piece_offset[0] + 1, self.piece_offset[1]]
        if not self.check_collision(self.current_piece, new_offset):
            self.piece_offset = new_offset
        else:
            self.merge()
            cleared = self.remove_full_lines()
            self.score += cleared * 100
            if cleared:
                self.speed = max(0.1, self.speed - 0.02)

            self._spawn_next_piece()

            if self.check_collision(self.current_piece, self.piece_offset):
                self.game_over = True


    def _spawn_next_piece(self):
        """Spawn the next piece at the top of the board."""
        self.current_piece = self.next_piece
        self.next_piece = choice(Tetris.SHAPES)
        self.piece_offset = [0, Tetris.WIDTH // 2 - len(self.current_piece[0]) // 2]


    def game_loop(self, stdscr):
        """Main game loop using curses."""
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        next_drop = time.time() + self.speed

        while not self.game_over:
            current_time = time.time()
            key = stdscr.getch()

            if key != -1:
                if self._handle_key(key) == 'quit':
                    break

            if current_time > next_drop:
                next_drop = time.time() + self.speed
                self._handle_drop()

            self.draw_board(stdscr)

        self._display_game_over(stdscr)
        return self.score


    def _handle_key(self, key):
        """Process a keyboard input key."""
        result = self.handle_input(key)
        if result == 'quit':
            return 'quit'
        return None


    def _handle_drop(self):
        """Handle automatic piece drop, collision, merging, and spawning new pieces."""
        new_offset = [self.piece_offset[0] + 1, self.piece_offset[1]]
        if not self.check_collision(self.current_piece, new_offset):
            self.piece_offset = new_offset
        else:
            self.merge()
            cleared = self.remove_full_lines()
            self.lines_cleared += cleared
            self.score += cleared * 100
            if cleared:
                self.speed = max(0.1, self.speed - 0.02)
            self._spawn_new_piece()
            if self.check_collision(self.current_piece, self.piece_offset):
                self.game_over = True


    def _spawn_new_piece(self):
        """Spawn the next piece and reset its position."""
        self.current_piece = self.next_piece
        self.next_piece = choice(Tetris.SHAPES)
        self.piece_offset = [0, Tetris.WIDTH // 2 - len(self.current_piece[0]) // 2]


    def _display_game_over(self, stdscr):
        """Display the game over screen."""
        if not self.game_over:
            return

        stdscr.clear()
        height, width = stdscr.getmaxyx()
        try:
            stdscr.addstr(height // 2 - 1, width // 2 - 5, "GAME OVER!")
            stdscr.addstr(height // 2, width // 2 - 8, f"Final Score: {self.score}")
            stdscr.addstr(height // 2 + 2, width // 2 - 10, "Press any key to continue...")
        except Exception as e:
            logging.error(f"Unexpected error in game over screen: {e}", exc_info=True)

        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()


    def build_game(self):
        """Run the interactive portion where the user provides moves."""

        print("\nStarting Tetris...")
        time.sleep(1)
        score = curses.wrapper(self.game_loop)
        return {
            "score": score,
            "lines_cleared": self.lines_cleared,
            "game_over": self.game_over
        }
    
    def evaluate(self, answer: Dict):
        """Evaluate the raw moves and return a structured result."""
        score = answer.get('score', 0)
        lines_cleared = answer.get('lines_cleared', 0)

        return {
            "score": score,
            "lines_cleared": lines_cleared,
            "passed": score >= 200  
        }
    
    def reward(self, result):
        """Convert evaluation results into currency/pet happiness rewards."""

        score = result.get('score', 0)
        lines_cleared = result.get('lines_cleared', 0)
        passed = result.get('passed', False)

        if passed:
            coins = 20 + (score // 100) * 5 + lines_cleared * 2
            pet_happiness = 10 + min(lines_cleared, 10) 
            print(f"\n🎉 Great job! You cleared {lines_cleared} lines!")
        else:
            coins = max(5, score // 50)  
            pet_happiness = 5
            print("\n💪 Keep practicing! You'll get better!")
        
        print(f"Reward: Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})")
        print(green(f"You received Rp. {'{:,}'.format(coins * 1000)} 🎉"))

        return {"currency": coins, "pet_happiness": pet_happiness}
    
    def play(self, player, pet):
        self.setup(player, pet)
        self.display_menu()
        self.build_question()
        choice = self.get_input()
        if choice.lower() == 'q':
            print("\nReturning to main menu...")
            return {"currency": 0, "pet_happiness": 0}
        
        summary = self.build_game()
        result = self.evaluate(summary)
        reward = self.reward(result)
        return reward

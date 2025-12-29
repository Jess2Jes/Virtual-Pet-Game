from .baseClass import MinigameStrategy
from typing import List
from .mathQuiz import MathQuiz
from .ticTacToe import TicTacToe
from .memoryMatch import MemoryMatch
from .battleContest import BattleContest
from .sudoku import Sudoku
from .tetris import Tetris
from .uno import Uno

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
    engine.register(Tetris())
    engine.register(Uno())
    return engine
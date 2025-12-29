from abc import ABC, abstractmethod
from typing import Any, Dict
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

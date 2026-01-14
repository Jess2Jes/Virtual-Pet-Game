# repositories/save_repository.py
from typing import Protocol, Dict, Any, Optional, List

class SaveRepository(Protocol):
    """
    Interface for saving and loading game data.
    Any class (JSON, SQL, Cloud) can implement this.
    """
    def save_game(self, username: str, game_state: Dict[str, Any]) -> bool: 
        ...

    def load_game(self, username: str) -> Optional[Dict[str, Any]]: 
        ...

    def delete_save(self, username: str) -> bool: 
        ...

    def list_saves(self) -> List[str]: 
        ...
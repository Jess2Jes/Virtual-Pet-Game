# features/memento.py

from typing import Dict, Any, List
from datetime import datetime

class GameMemento:
    """Stores the state of the game."""
    
    def __init__(self, user_data: Dict[str, Any], game_data: Dict[str, Any]):
        self._user_data = user_data
        self._game_data = game_data
        self._timestamp = datetime.now()
    
    def get_user_data(self) -> Dict[str, Any]:
        return self._user_data. copy()
    
    def get_game_data(self) -> Dict[str, Any]:
        return self._game_data.copy()
    
    def get_timestamp(self) -> datetime:
        return self._timestamp


class PetMemento:
    """Stores the state of a pet."""
    
    def __init__(self, pet_data: Dict[str, Any]):
        self._state = pet_data. copy()
    
    def get_state(self) -> Dict[str, Any]:
        return self._state.copy()


class UserMemento:
    """Stores the state of a user."""
    
    def __init__(self, user_data: Dict[str, Any], pets_data: List[Dict[str, Any]]):
        self._user_data = user_data. copy()
        self._pets_data = [pet.copy() for pet in pets_data]
    
    def get_user_data(self) -> Dict[str, Any]:
        return self._user_data. copy()
    
    def get_pets_data(self) -> List[Dict[str, Any]]:
        return [pet.copy() for pet in self._pets_data]
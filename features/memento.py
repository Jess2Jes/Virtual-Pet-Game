# features/memento.py
from typing import Dict, Any, List
from datetime import datetime

"""
memento.py

Simple Memento pattern helpers used for saving and restoring snapshots of
the game, user, and pet state.

This module provides three lightweight container classes:
- GameMemento: contains a snapshot of user-level and global game data with a timestamp.
- PetMemento: contains a snapshot of a single pet's state.
- UserMemento: contains a snapshot of user data and a list of pet snapshots.

All returned dicts are shallow copies to help avoid accidental mutation of the
stored snapshot data by callers. These classes are intended to be immutable
containers once constructed (no setters provided).
"""


class GameMemento:
    """Immutable snapshot of the game's state at a point in time.

    Stores:
      - user_data: a mapping representing the user's saved attributes (e.g., inventory, currency).
      - game_data: a mapping representing global or game-session specific data.
      - timestamp: datetime when the memento was created.

    Use get_user_data() / get_game_data() to obtain copies of the stored dictionaries.
    """
    def __init__(self, user_data: Dict[str, Any], game_data: Dict[str, Any]):
        self._user_data = user_data
        self._game_data = game_data
        self._timestamp = datetime.now()

    def get_user_data(self) -> Dict[str, Any]:
        """Return a shallow copy of the stored user data mapping."""
        return self._user_data.copy()

    def get_game_data(self) -> Dict[str, Any]:
        """Return a shallow copy of the stored game data mapping."""
        return self._game_data.copy()

    def get_timestamp(self) -> datetime:
        """Return the datetime when this memento was created."""
        return self._timestamp


class PetMemento:
    """Snapshot container for a single pet's state.

    The constructor expects a dictionary containing the pet attributes to preserve.
    get_state() returns a shallow copy of that dictionary.
    """
    def __init__(self, pet_data: Dict[str, Any]):
        self._state = pet_data.copy()

    def get_state(self) -> Dict[str, Any]:
        """Return a shallow copy of the stored pet state."""
        return self._state.copy()


class UserMemento:
    """Snapshot container for a user and their pets.

    Stores a copy of user-level data and an independent list-of-dicts describing each pet.
    Use get_user_data() and get_pets_data() to retrieve copies suitable for restoration.
    """
    def __init__(self, user_data: Dict[str, Any], pets_data: List[Dict[str, Any]]):
        self._user_data = user_data.copy()
        # Ensure we copy each pet dict so the snapshot is isolated from external mutation
        self._pets_data = [pet.copy() for pet in pets_data]

    def get_user_data(self) -> Dict[str, Any]:
        """Return a shallow copy of the saved user data."""
        return self._user_data.copy()

    def get_pets_data(self) -> List[Dict[str, Any]]:
        """Return a deep-ish copy (list of shallow-copied dicts) of the saved pets data."""
        return [pet.copy() for pet in self._pets_data]
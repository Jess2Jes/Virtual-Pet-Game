"""
repositories/save_manager.py

JSON-backed persistence implementation for saving and loading player game state.

This module keeps the public `SaveManager` API intact (including singleton access)
while delegating file I/O mechanics to a dedicated repository implementation.
The goal is to preserve 100% identical runtime behavior while improving SRP/DIP:
- `JsonFileSaveRepository` implements the `SaveRepository` persistence contract.
- `SaveManager` remains the singleton entry point used by the rest of the app.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from repositories.save_repository import SaveRepository


class JsonFileSaveRepository(SaveRepository):
    """
    File-based SaveRepository using a single JSON file mapping username -> game state.

    Collaboration:
    - Used by `SaveManager` as its persistence backend.
    - Encapsulates disk I/O, JSON encoding/decoding, and save-file initialization.
    """

    def __init__(self, save_directory: Path | str = "saves", filename: str = "player_saves.json"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        self.save_file = self.save_directory / filename

    def save_game(self, username: str, game_state: Dict[str, Any]) -> bool:
        """
        Save game state for a specific user.

        Behavior is intentionally preserved: prints the same success/error messages and
        stores a `last_saved` ISO timestamp in the persisted mapping.
        """
        try:
            all_saves = self._load_all_saves()
            game_state["last_saved"] = datetime.now().isoformat()
            all_saves[username] = game_state
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(all_saves, f, indent=4, ensure_ascii=False)

            print(f"\n✅ Game saved successfully for {username}!")
            return True

        except Exception as e:
            print(f"\n❌ Error saving game: {e}")
            return False

    def load_game(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Load the saved game state for a specific user.

        Behavior is intentionally preserved: prints the same success/missing/error messages.
        """
        try:
            all_saves = self._load_all_saves()

            if username in all_saves:
                print(f"\n✅ Game loaded successfully for {username}!")
                return all_saves[username]
            else:
                print(f"\n⚠️ No save file found for {username}.")
                return None

        except Exception as e:
            print(f"❌ Error loading game: {e}")
            return None

    def delete_save(self, username: str) -> bool:
        """
        Delete the save entry for the given username.

        Behavior is intentionally preserved: prints the same success/missing/error messages.
        """
        try:
            all_saves = self._load_all_saves()

            if username in all_saves:
                del all_saves[username]

                with open(self.save_file, "w", encoding="utf-8") as f:
                    json.dump(all_saves, f, indent=4, ensure_ascii=False)

                print(f"\n✅ Save deleted for {username}!")
                return True
            else:
                print(f"\n⚠️ No save found for {username}.")
                return False

        except Exception as e:
            print(f"\n❌ Error deleting save: {e}")
            return False

    def list_saves(self) -> list:
        """Return a list of usernames for which saves exist."""
        all_saves = self._load_all_saves()
        return list(all_saves.keys())

    def _load_all_saves(self) -> Dict[str, Any]:
        """
        Load and return the complete save mapping from disk.

        Returns an empty dict if the save file does not exist or is corrupt.
        """
        if not self.save_file.exists():
            return {}

        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}


class SaveManager(SaveRepository):
    """
    Singleton save manager used by the rest of the application.

    Collaboration:
    - Exposes the same public API as before (`get_instance`, `save_game`, `load_game`, etc.).
    - Delegates persistence to `JsonFileSaveRepository` to separate I/O from lifecycle concerns.
    """

    _instance: Optional["SaveManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SaveManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, repo: SaveRepository | None = None):
        # Idempotent init: keep old singleton semantics.
        if getattr(self, "_initialized", False):
            return
        self._repo: SaveRepository = repo or JsonFileSaveRepository()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "SaveManager":
        """Return the global SaveManager singleton instance, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_game(self, username: str, game_state: Dict[str, Any]) -> bool:
        """Persist state for a user via the configured repository backend."""
        return self._repo.save_game(username, game_state)

    def load_game(self, username: str) -> Optional[Dict[str, Any]]:
        """Load persisted state for a user via the configured repository backend."""
        return self._repo.load_game(username)

    def delete_save(self, username: str) -> bool:
        """Delete a user's persisted state via the configured repository backend."""
        return self._repo.delete_save(username)

    def list_saves(self) -> list:
        """Return a list of usernames for which saves exist."""
        return self._repo.list_saves()

    # Compatibility: some callers reach into the old private API.
    def _load_all_saves(self) -> Dict[str, Any]:
        """
        Backwards-compatible private API used elsewhere in the codebase.

        Preserves behavior by forwarding to the underlying JSON repository.
        """
        if isinstance(self._repo, JsonFileSaveRepository):
            return self._repo._load_all_saves()
        # Fallback for alternate implementations: best-effort empty mapping.
        return {}
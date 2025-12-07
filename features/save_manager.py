# features/save_manager.py
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

"""
save_manager.py

Singleton SaveManager responsible for saving, loading, deleting, and listing
player save data as JSON in the `saves/player_saves.json` file.

Design notes:
- Implements a simple singleton pattern so callers can obtain SaveManager.get_instance()
  and operate on the single shared save file.
- Saves are stored as a mapping username -> game_state dict. Each saved state is
  annotated with a 'last_saved' ISO timestamp.
- The implementation is tolerant of missing/corrupt save files and returns empty
  mappings in those cases.

Changes:
- Translated inline comments to English and added module/class/method docstrings.
- Fixed minor whitespace typos in attribute access (self.save_directory / self.save_file).
  No behavioral changes were made.
"""


class SaveManager:
    """Singleton class to manage game saves on disk."""

    _instance: Optional["SaveManager"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SaveManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the save directory and file on first construction.

        The constructor is idempotent: subsequent instantiations reuse the same
        underlying save directory/file information.
        """
        if not SaveManager._initialized:
            # create folder 'saves' if it does not exist
            self.save_directory = Path("saves")
            self.save_directory.mkdir(exist_ok=True)
            self.save_file = self.save_directory / "player_saves.json"
            SaveManager._initialized = True

    @classmethod
    def get_instance(cls) -> "SaveManager":
        """Return the global SaveManager singleton instance, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_game(self, username: str, game_state: Dict[str, Any]) -> bool:
        """
        Save game state for a specific user.

        The provided game_state mapping will be stored under the username key and
        annotated with a 'last_saved' ISO timestamp.

        Returns:
            True on success, False on failure.
        """
        try:
            # Load existing saves
            all_saves = self._load_all_saves()

            # Add timestamp
            game_state["last_saved"] = datetime.now().isoformat()

            # Update user's save
            all_saves[username] = game_state

            # Write to file
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

        Returns:
            The saved mapping if present, otherwise None.
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

        Returns:
            True if a save was removed, False if none existed or on error.
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
            # Corrupted file -> treat as no saves
            return {}
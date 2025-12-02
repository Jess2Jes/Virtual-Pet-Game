# features/save_manager.py

import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class SaveManager:
    """Singleton class to manage game saves."""
    
    _instance: Optional['SaveManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SaveManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SaveManager._initialized:
            self. save_directory = Path("saves") # create folder 'saves' if not exists
            self.save_directory.mkdir(exist_ok=True) # check and create directory
            self.save_file = self.save_directory / "player_saves.json"
            SaveManager._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'SaveManager':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def save_game(self, username: str, game_state: Dict[str, Any]) -> bool:
        """Save game state for a specific user."""
        try:
            # Load existing saves
            all_saves = self._load_all_saves()
            
            # Add timestamp
            game_state['last_saved'] = datetime.now().isoformat()
            
            # Update user's save
            all_saves[username] = game_state
            
            # Write to file
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(all_saves, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Game saved successfully for {username}!")
            return True
            
        except Exception as e:
            print(f"❌ Error saving game: {e}")
            return False
    
    def load_game(self, username: str) -> Optional[Dict[str, Any]]:
        """Load game state for a specific user."""
        try:
            all_saves = self._load_all_saves()
            
            if username in all_saves:
                print(f"✅ Game loaded successfully for {username}!")
                return all_saves[username]
            else:
                print(f"⚠️ No save file found for {username}.")
                return None
                
        except Exception as e:
            print(f"❌ Error loading game: {e}")
            return None
    
    def delete_save(self, username: str) -> bool:
        """Delete save for a specific user."""
        try:
            all_saves = self._load_all_saves()
            
            if username in all_saves:
                del all_saves[username]
                
                with open(self.save_file, 'w', encoding='utf-8') as f:
                    json.dump(all_saves, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Save deleted for {username}!")
                return True
            else:
                print(f"⚠️ No save found for {username}.")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting save: {e}")
            return False
    
    def list_saves(self) -> list:
        """List all available saves."""
        all_saves = self._load_all_saves()
        return list(all_saves.keys())
    
    def _load_all_saves(self) -> Dict[str, Any]:
        """Load all saves from file."""
        if not self.save_file.exists():
            return {}
        
        try:
            with open(self. save_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
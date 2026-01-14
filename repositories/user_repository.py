from typing import Dict, Optional, List
from features.user import User

class UserRepository:
    """
    Manages the collection of User entities. 
    Acts as an abstraction over the storage (memory/file).
    """
    def __init__(self):
        # This replaces the global User.users dictionary
        self._users: Dict[str, User] = {} 

    def add(self, user: User) -> None:
        """Adds a new user to the repository."""
        key = user.username.casefold()
        if key in self._users:
            raise ValueError(f"User {user.username} already exists.")
        self._users[key] = user

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieves a user by username (case-insensitive)."""
        key = username.casefold()
        return self._users.get(key)

    def get_all(self) -> List[User]:
        """Returns a list of all users."""
        return list(self._users.values())

    def exists(self, username: str) -> bool:
        """Checks if a user exists."""
        return username.casefold() in self._users
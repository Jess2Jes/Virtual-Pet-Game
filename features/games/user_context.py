"""
features/user_context.py

User context boundary used to normalize legacy global access (`User.current_user`)
without changing runtime behavior.

Responsibilities:
- Provide an injectable, explicit way to access the "current user" preferences dicts.
- Preserve legacy behavior by writing through to `User.current_user` if present.

Collaboration:
- `features.game.Game` and topic handlers depend on `UserContext` instead of directly touching globals.
"""

from __future__ import annotations

from typing import Any, Dict, Protocol


class UserContext(Protocol):
    """Abstraction for accessing the current user's preference capture containers."""
    def music(self) -> Dict[str, Any]: ...
    def food(self) -> Dict[str, Any]: ...


class LegacyUserContext:
    """
    Compatibility user-context that preserves the original behavior.

    If the legacy global `User.current_user` exists, it is used as the write target.
    Otherwise, it falls back to the injected `user` instance.
    """

    def __init__(self, user):
        self._user = user

    def _target(self):
        # Preserve original semantics: code previously wrote to User.current_user.*
        # If the attribute is missing, we fall back to the provided user.
        from features.user import User  # Avoid circular import
        return getattr(User, "current_user", None) or self._user

    def music(self) -> Dict[str, Any]:
        return self._target().music

    def food(self) -> Dict[str, Any]:
        return self._target().food
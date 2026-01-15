"""
utils/ports.py

I/O and content-loading ports used throughout the application.

Responsibilities:
- Define port Protocols (DIP) that decouple business logic from console/file I/O.
- Provide concrete adapters for console I/O and file-based JSON content loading.

Collaboration:
- `IOPort` is the unified interface required by refactored game logic (read + write).
- `ConsoleIO` implements `IOPort`.
- `ContentLoader` is a Protocol; concrete implementations (e.g. `FileContentLoader`) must be injected.
"""

from __future__ import annotations

from json import load
from typing import Protocol


class InputPort(Protocol):
    """Abstract input port for reading user data."""
    def read(self, prompt: str = "") -> str: ...


class OutputPort(Protocol):
    """Abstract output port for emitting messages."""
    def write(self, message: str) -> None: ...


class IOPort(InputPort, OutputPort, Protocol):
    """
    Unified interactive I/O port (read + write).

    Collaboration:
    - Used by the refactored `features.game.Game` to avoid `InputPort | OutputPort` mismatch.
    - Implemented by `ConsoleIO` and can be implemented by test doubles.
    """
    pass


class ConsoleIO(IOPort):
    """Console-based I/O adapter."""
    def read(self, prompt: str = "") -> str:
        """Read input from the console."""
        return input(prompt)

    def write(self, message: str) -> None:
        """Write a message to the console."""
        print(message)


class ContentLoader(Protocol):
    """Abstract loader for retrieving structured content."""
    def load_json(self, path: str) -> list: ...


class FileContentLoader:
    """Filesystem-based JSON content loader."""
    def load_json(self, path: str) -> list:
        with open(path, "r", encoding="utf-8") as f:
            return load(f)
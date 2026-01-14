from typing import Protocol
from json import load

class InputPort(Protocol):
    """Abstract input port for reading user data."""
    def read(self, prompt: str = "") -> str: ...

class OutputPort(Protocol):
    """Abstract output port for emitting messages."""
    def write(self, message: str) -> None: ...

class ConsoleIO(InputPort, OutputPort):
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

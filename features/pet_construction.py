"""
features/pet_construction.py

Centralized, behavior-preserving pet construction utilities.

This module exists to normalize pet construction boundaries (LSP/DIP) without
changing any gameplay rules:
- `NullOutputPort` preserves the "no output" semantics for restored pets when no IO
  is available, without raising in AbstractPet.
- `PetBuilder` is an injectable collaborator that constructs pets consistently.
"""

from __future__ import annotations

from typing import Protocol

from utils.ports import OutputPort


class NullOutputPort(OutputPort):
    """
    OutputPort that discards all messages.

    Collaboration:
    - Used by pet factories/restoration flows when no interactive OutputPort is available.
    - Avoids changing gameplay logic while satisfying AbstractPet's IO requirement.
    """

    def write(self, message: str) -> None:  # pragma: no cover (side-effect sink)
        return


class PetBuilder(Protocol):
    """Factory boundary for creating pet entities with a guaranteed OutputPort."""

    def create(self, pet_type: str, name: str, age: float, io: OutputPort | None = None):
        ...


class DefaultPetBuilder:
    """
    Default PetBuilder used by the application.

    Collaboration:
    - Used by `features.user.DefaultPetFactory` and any restoration code.
    - Responsible only for selecting the pet class and injecting an OutputPort.
    """

    def __init__(self, default_io: OutputPort | None = None):
        from features.animal import Cat, Rabbit, Dino, Dragon, Pou

        self._pet_class_map = {
            "Cat": Cat,
            "Rabbit": Rabbit,
            "Dinosaur": Dino,
            "Dragon": Dragon,
            "Pou": Pou,
        }
        self._default_cls = Cat
        self._default_io = default_io

    def create(self, pet_type: str, name: str, age: float, io: OutputPort | None = None):
        cls = self._pet_class_map.get(pet_type, self._default_cls)
        effective_io = io or self._default_io or NullOutputPort()
        return cls(name, age, io=effective_io)
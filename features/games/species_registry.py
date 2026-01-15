"""
features/species_registry.py

Species creation boundary for the game.

Responsibilities:
- Map UI choices ("1".."5") to concrete pet constructors.
- Ensure a single IO invariant: created pets always receive the current IOPort.

Collaboration:
- Injected into `features.game.Game` to remove hard-coded species branching (OCP/DIP).
"""

from __future__ import annotations

from typing import Callable, Dict, Protocol

from utils.ports import IOPort

from features.animal import Cat, Rabbit, Dino, Dragon, Pou
from features.pet import VirtualPet


class SpeciesRegistry(Protocol):
    """Factory/registry boundary for producing pets from a menu selection."""
    def create(self, selection: str, name: str, io: IOPort) -> VirtualPet | None: ...


class DefaultSpeciesRegistry:
    """Default registry mapping the existing menu numbers to existing species classes."""

    def __init__(self):
        self._factories: Dict[str, Callable[[str, IOPort], VirtualPet]] = {
            "1": lambda name, io: Cat(name, 0, io=io),
            "2": lambda name, io: Rabbit(name, 0, io=io),
            "3": lambda name, io: Dino(name, 0, io=io),
            "4": lambda name, io: Dragon(name, 0, io=io),
            "5": lambda name, io: Pou(name, 0, io=io),
        }

    def create(self, selection: str, name: str, io: IOPort) -> VirtualPet | None:
        factory = self._factories.get(selection)
        if not factory:
            return None
        return factory(name, io)
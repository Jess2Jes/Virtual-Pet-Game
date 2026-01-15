"""
features/animal.py

Concrete pet species implementations.

Responsibilities:
- Provide per-species identity attributes (emoji, favorite food, music preferences).
- Provide lifecycle ASCII art rendering helpers.

Collaboration:
- Inherits core behavior from `features.pet.VirtualPet`.
- Uses `utils.ports.OutputPort` for output and `constants.animalsArt` for ASCII art.
"""

from __future__ import annotations

from constants.configs import UIConfig as UIC
from constants.animalsArt import (
    CatsArt as CAT,
    RabbitsArt as RABBIT,
    DinoArt as DINO,
    DragonArt as DRAGON,
    PouArt as POU,
)
from utils.ports import OutputPort

from .pet import VirtualPet


class PetIdentity:
    """Identity attributes shared across pet behaviors (pure data container)."""

    def __init__(self, emoji: str, fav_food: str, music_taste: str, dislike_music: str, songs: tuple[str, ...]):
        self.emoji = emoji
        self.fav_food = fav_food
        self.music_taste = music_taste
        self.dislike_music = dislike_music
        self.songs = songs


class IdentityMixin:
    """Shared identity assignment helper to avoid repetition across species."""

    def _set_identity(self, identity: PetIdentity) -> None:
        self.emoji = identity.emoji
        self.fav_food = identity.fav_food
        self.music_taste = identity.music_taste
        self.dislike_music = identity.dislike_music
        self.songs = identity.songs


class PetRenderer:
    """Rendering helper for producing lifecycle ASCII art blocks."""

    @staticmethod
    def render(art: str):
        yield UIC.LINE
        yield art


class Cat(IdentityMixin, VirtualPet):
    """Cat species implementation (identity + art)."""

    def __init__(self, name, age, io: OutputPort = None):
        # Preserve call pattern used by the existing codebase.
        super().__init__(name=name, io=io, age=age, species="Cat")
        self._set_identity(
            PetIdentity(
                emoji="🐈",
                fav_food="Chicken",
                music_taste="Pop",
                dislike_music="Reggae",
                songs=("Born Again by Doja Cat", "Golden by HUNTR/X", "Busy Woman by Sabrina Carpenter"),
            )
        )

    @staticmethod
    def baby():
        yield from PetRenderer.render(CAT.baby)

    @staticmethod
    def teen():
        yield from PetRenderer.render(CAT.teenager)

    @staticmethod
    def adult():
        yield from PetRenderer.render(CAT.adult)

    @staticmethod
    def elder():
        yield from PetRenderer.render(CAT.elder)


class Rabbit(IdentityMixin, VirtualPet):
    """Rabbit species implementation (identity + art)."""

    def __init__(self, name, age, io: OutputPort = None):
        super().__init__(name=name, io=io, age=age, species="Rabbit")
        self._set_identity(
            PetIdentity(
                emoji="🐇",
                fav_food="Ice Cream",
                music_taste="J-Pop",
                dislike_music="Rock",
                songs=("Genic - It's Showtime", "Kis-My-Ft2 - Glory Days", "TWS - Hajimemashite"),
            )
        )

    @staticmethod
    def baby():
        yield from PetRenderer.render(RABBIT.baby)

    @staticmethod
    def teen():
        yield from PetRenderer.render(RABBIT.teenager)

    @staticmethod
    def adult():
        yield from PetRenderer.render(RABBIT.adult)

    @staticmethod
    def elder():
        yield from PetRenderer.render(RABBIT.elder)


class Dino(IdentityMixin, VirtualPet):
    """Dinosaur species implementation (identity + art)."""

    def __init__(self, name, age, io: OutputPort = None):
        super().__init__(name=name, io=io, age=age, species="Dinosaur")
        self._set_identity(
            PetIdentity(
                emoji="🦖",
                fav_food="French Fries",
                music_taste="K-Pop",
                dislike_music="Country",
                songs=("BTS - Spring Day", "Fifty Fifty - Cupid", "Twice - The Feels"),
            )
        )

    @staticmethod
    def baby():
        yield from PetRenderer.render(DINO.baby)

    @staticmethod
    def teen():
        yield from PetRenderer.render(DINO.teenager)

    @staticmethod
    def adult():
        yield from PetRenderer.render(DINO.adult)

    @staticmethod
    def elder():
        yield from PetRenderer.render(DINO.elder)


class Dragon(IdentityMixin, VirtualPet):
    """Dragon species implementation (identity + art)."""

    def __init__(self, name, age, io: OutputPort = None):
        super().__init__(name=name, io=io, age=age, species="Dragon")
        self._set_identity(
            PetIdentity(
                emoji="🐉",
                fav_food="Nugget",
                music_taste="Blues",
                dislike_music="K-Pop",
                songs=("The Thrill is Gone By BB King", "Mannish Boy By Muddy Waters", "Love in Vain By Robert Johnson"),
            )
        )

    @staticmethod
    def baby():
        yield from PetRenderer.render(DRAGON.baby)

    @staticmethod
    def teen():
        yield from PetRenderer.render(DRAGON.teenager)

    @staticmethod
    def adult():
        yield from PetRenderer.render(DRAGON.adult)

    @staticmethod
    def elder():
        yield from PetRenderer.render(DRAGON.elder)


class Pou(IdentityMixin, VirtualPet):
    """Pou species implementation (identity + art)."""

    def __init__(self, name, age, io: OutputPort = None):
        super().__init__(name=name, io=io, age=age, species="Pou")
        self._set_identity(
            PetIdentity(
                emoji="💩",
                fav_food="Chicken",
                music_taste="Jazz",
                dislike_music="Rap",
                songs=("Modern Jazz Quartet - Django", "Ahmad Jamal - Poinciana", "George Shearing - Lullaby of Birdland"),
            )
        )

    @staticmethod
    def baby():
        yield from PetRenderer.render(POU.baby)

    @staticmethod
    def teen():
        yield from PetRenderer.render(POU.teenager)

    @staticmethod
    def adult():
        yield from PetRenderer.render(POU.adult)

    @staticmethod
    def elder():
        yield from PetRenderer.render(POU.elder)
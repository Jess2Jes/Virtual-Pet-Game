"""Animal entities with separated identity data and rendering concerns.

"""

from .pet import VirtualPet
from constants.configs import LINE
from constants.animalsArt import (
    CatsArt as CAT,
    RabbitsArt as RABBIT,
    DinoArt as DINO,
    DragonArt as DRAGON,
    PouArt as POU,
)


class PetIdentity:
    """Encapsulates identity attributes shared across pet behaviors."""
    def __init__(self, emoji: str, fav_food: str, music_taste: str, dislike_music: str, songs: tuple[str, ...]):
        self.emoji = emoji
        self.fav_food = fav_food
        self.music_taste = music_taste
        self.dislike_music = dislike_music
        self.songs = songs


class IdentityMixin:
    """Shared identity assignment helper to avoid repetition."""
    def _set_identity(self, identity: PetIdentity):
        self.emoji = identity.emoji
        self.fav_food = identity.fav_food
        self.music_taste = identity.music_taste
        self.dislike_music = identity.dislike_music
        self.songs = identity.songs


class PetRenderer:
    """Responsible for rendering ASCII representations."""
    @staticmethod
    def render(art: str):
        yield LINE
        yield art


class Cat(IdentityMixin, VirtualPet):
    def __init__(self, name, age):
        super().__init__(name, age, "Cat")
        self._set_identity(PetIdentity(
            emoji="🐈",
            fav_food="Chicken",
            music_taste="Pop",
            dislike_music="Reggae",
            songs=("Born Again by Doja Cat", "Golden by HUNTR/X", "Busy Woman by Sabrina Carpenter"),
        ))

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
    def __init__(self, name, age):
        super().__init__(name, age, "Rabbit")
        self._set_identity(PetIdentity(
            emoji="🐇",
            fav_food="Ice Cream",
            music_taste="J-Pop",
            dislike_music="Rock",
            songs=("Genic - It's Showtime", "Kis-My-Ft2 - Glory Days", "TWS - Hajimemashite"),
        ))

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
    def __init__(self, name, age):
        super().__init__(name, age, "Dinosaur")
        self._set_identity(PetIdentity(
            emoji="🦖",
            fav_food="French Fries",
            music_taste="K-Pop",
            dislike_music="Country",
            songs=("BTS - Spring Day", "Fifty Fifty - Cupid", "Twice - The Feels"),
        ))

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
    def __init__(self, name, age):
        super().__init__(name, age, "Dragon")
        self._set_identity(PetIdentity(
            emoji="🐉",
            fav_food="Nugget",
            music_taste="Blues",
            dislike_music="K-Pop",
            songs=("The Thrill is Gone By BB King", "Mannish Boy By Muddy Waters", "Love in Vain By Robert Johnson"),
        ))

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
    def __init__(self, name, age):
        super().__init__(name, age, "Pou")
        self._set_identity(PetIdentity(
            emoji="💩",
            fav_food="Chicken",
            music_taste="Jazz",
            dislike_music="Rap",
            songs=("Modern Jazz Quartet - Django", "Ahmad Jamal - Poinciana", "George Shearing - Lullaby of Birdland"),
        ))

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
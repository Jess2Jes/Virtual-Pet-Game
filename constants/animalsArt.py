from typing import Protocol
from .arts.cats import baby_cat, teenager_cat, adult_cat, elder_cat
from .arts.rabbits import baby_rabbits, teenager_rabbits, adult_rabbits, elder_rabbits
from .arts.dino import baby_dino, teenager_dino, adult_dino, elder_dino
from .arts.dragon import baby_dragon, teenager_dragon, adult_dragon, elder_dragon
from .arts.pou import baby_pou, teenager_pou, adult_pou, elder_pou

class AnimalArtProtocol(Protocol):
    """
    Protocol for animal ASCII art representations.
    """
    baby: str
    teenager: str
    adult: str
    elder: str
    
class CatsArt(AnimalArtProtocol): 
    """
    Contains ASCII art representations of cats.
    """
    baby = baby_cat
    teenager = teenager_cat
    adult = adult_cat
    elder = elder_cat
    
class RabbitsArt(AnimalArtProtocol): 
    """
    Contains ASCII art representations of rabbits.
    """
    baby = baby_rabbits
    teenager = teenager_rabbits
    adult = adult_rabbits
    elder = elder_rabbits

class DinoArt(AnimalArtProtocol): 
    """
    Contains ASCII art representations of dinosaurs.
    """
    baby = baby_dino
    teenager = teenager_dino
    adult = adult_dino
    elder = elder_dino
    
class DragonArt(AnimalArtProtocol): 
    """
    Contains ASCII art representations of dragons.
    """
    baby = baby_dragon
    teenager = teenager_dragon
    adult = adult_dragon
    elder = elder_dragon
    
class PouArt(AnimalArtProtocol): 
    """
    Contains ASCII art representations of pous.
    """
    baby = baby_pou
    teenager = teenager_pou
    adult = adult_pou
    elder = elder_pou
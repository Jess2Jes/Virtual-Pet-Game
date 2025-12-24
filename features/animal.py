from .pet import VirtualPet
from .formatter import GARIS
from constants.animalsArt import (
    CatsArt as CAT,
    RabbitsArt as RABBIT,
    DinoArt as DINO,
    DragonArt as DRAGON,
    PouArt as POU,
    )

class Cat(VirtualPet):
    def __init__(self, name, age):
        super().__init__(name, age, "Cat")
        self.emoji = "🐈"
        self.fav_food = "Chicken"
        self.music_taste = "Pop"
        self.dislike_music = "Reggae"
        self.songs = "Born Again by Doja Cat", "Golden by HUNTR/X", "Busy Woman by Sabrina Carpenter"
    
    @staticmethod
    async def baby():

        yield GARIS
        yield CAT.baby
    
    @staticmethod
    async def teen(): 

        yield GARIS
        yield CAT.teenager
    
    @staticmethod
    async def adult(): 

        yield GARIS
        yield CAT.adult
        
    @staticmethod
    async def elder(): 

        yield GARIS
        yield 


class Rabbit(VirtualPet):
    def __init__(self, name, age):
        super().__init__(name, age, "Rabbit")
        self.emoji = "🐇"
        self.fav_food = "Ice Cream"
        self.music_taste = "J-Pop"
        self.dislike_music = "Rock"
        self.songs = "Genic - It's Showtime", "Kis-My-Ft2 - Glory Days", "TWS - Hajimemashite"
    
    @staticmethod
    async def baby():

       yield GARIS
       yield RABBIT.baby
    
    @staticmethod
    async def teen(): 

        yield GARIS
        yield RABBIT.teenager
    
    @staticmethod
    async def adult(): 

        yield GARIS
        yield RABBIT.adult
        
    @staticmethod
    async def elder(): 

        yield GARIS
        yield RABBIT.elder

class Dino(VirtualPet):
    def __init__(self, name, age):
        super().__init__(name, age, "Dinosaur")
        self.emoji = "🦖"
        self.fav_food = "French Fries"
        self.music_taste = "K-Pop"
        self.dislike_music = "Country"
        self.songs = "BTS - Spring Day", "Fifty Fifty - Cupid", "Twice - The Feels"
    
    @staticmethod
    async def baby():

       yield GARIS
       yield DINO.baby
    
    @staticmethod
    async def teen(): 
        yield GARIS
        yield DINO.teenager
    
    @staticmethod
    async def adult():  

        yield GARIS
        yield DINO.adult

    @staticmethod
    async def elder():  

        yield GARIS
        yield DINO.elder
        
    
class Dragon(VirtualPet):
    def __init__(self, name, age):
        super().__init__(name, age, "Dragon")
        self.emoji = "🐉"
        self.fav_food = "Nugget"
        self.music_taste = "Blues"
        self.dislike_music = "K-Pop"
        self.songs = "The Thrill is Gone By BB King", "Mannish Boy By Muddy Waters", "Love in Vain By Robert Johnson"
    
    @staticmethod
    async def baby():  

        yield GARIS
        yield DRAGON.baby
    
    @staticmethod
    async def teen():  

       yield GARIS
       yield DRAGON.teenager
    
    @staticmethod
    async def adult():  

        yield GARIS
        yield DRAGON.adult
        
    @staticmethod
    async def elder(): 
        
        yield GARIS
        yield DRAGON.elder
        
class Pou(VirtualPet):
    def __init__(self, name, age):
        super().__init__(name, age, "Pou")
        self.emoji = "💩"
        self.fav_food = "Chicken"
        self.music_taste = "Jazz"
        self.dislike_music = "Rap"
        self.songs = "Modern Jazz Quartet - Django", "Ahmad Jamal - Poinciana", "George Shearing - Lullaby of Birdland"
    
    @staticmethod
    async def baby(): 
        yield GARIS
        yield POU.baby
    
    @staticmethod
    async def teen():  
        yield GARIS
        yield POU.teenager
        
    @staticmethod  
    async def adult():  
        yield GARIS
        yield POU.adult
    
    @staticmethod
    async def elder():  

        yield GARIS
        yield POU.elder
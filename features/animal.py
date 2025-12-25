from .pet import VirtualPet
from constants.configs import LINE
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
    def baby():

        yield LINE
        yield CAT.baby
    
    @staticmethod
    def teen(): 

        yield LINE
        yield CAT.teenager
    
    @staticmethod
    def adult(): 

        yield LINE
        yield CAT.adult
        
    @staticmethod
    def elder(): 

        yield LINE
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
    def baby():

       yield LINE
       yield RABBIT.baby
    
    @staticmethod
    def teen(): 

        yield LINE
        yield RABBIT.teenager
    
    @staticmethod
    def adult(): 

        yield LINE
        yield RABBIT.adult
        
    @staticmethod
    def elder(): 

        yield LINE
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
    def baby():

       yield LINE
       yield DINO.baby
    
    @staticmethod
    async def teen(): 
        yield LINE
        yield DINO.teenager
    
    @staticmethod
    def adult():  

        yield LINE
        yield DINO.adult

    @staticmethod
    def elder():  

        yield LINE
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
    def baby():  

        yield LINE
        yield DRAGON.baby
    
    @staticmethod
    def teen():  

       yield LINE
       yield DRAGON.teenager
    
    @staticmethod
    def adult():  

        yield LINE
        yield DRAGON.adult
        
    @staticmethod
    def elder(): 
        
        yield LINE
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
    def baby(): 
        yield LINE
        yield POU.baby
    
    @staticmethod
    def teen():  
        yield LINE
        yield POU.teenager
        
    @staticmethod  
    def adult():  
        yield LINE
        yield POU.adult
    
    @staticmethod
    def elder():  

        yield LINE
        yield POU.elder
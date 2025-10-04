English | [Indonesian](READMEID.md) | [中文](READMECN.md)
# 🐾 Virtual Pet Game

A console-based virtual pet game built with OOP.  

## 📖 Overview
- User system with login and registration  
- Multiple pets (Cat, Rabbit, Dinosaur, Dragon, Pou)  
- Pet care: feed, bathe, heal, sleep, walk, play, talk  
- Shop with in-game currency and items  
- Life stages: baby → teen → adult → elder  
- Stats that affect survival: happiness, hunger, sanity, health, fat, energy  

## ✨ Features
- **Users**: authentication and currency  
- **Pets**: random stats, aging, ASCII art by stage  
- **Interactions**: feeding, bathing, walking, potions, more  
- **Shop**: foods, soaps, potions with effects  
- **Status UI**: formatted CLI display  
- **Time**: in-game clock and day counter  

## 📂 Project structure
- `main.py` – entry point, menus, session state.  
- `game.py` – gameplay loop, pet interactions.  
- `pet.py` – VirtualPet class, stats, aging, shared stock.  
- `animal.py` – subclasses for each species with ASCII art.  
- `formatter.py` – text truncation and status box formatter.  
- `shop.py` – item catalog, purchase logic.  
- `user.py` – user registry, authentication, currency.  

For detailed docs, see [docs/structure.md](docs/structure.md)

## 🎮 Run the game

1. Install **Python 3.x**.  
2. Clone or fork the repository:  
   ```bash
   git clone https://github.com/Jess2Jes/Virtual-Pet-Game.git
   cd Virtual-Pet-Game
3. Run `python main.py`


## 🚀 Roadmap

- Save/load pets and users (JSON, pickle, or database).
- GUI (Tkinter, PyQT, or web with Flask/FastAPI).
- More animals and ASCII art animations.
- Mini-games and events.
- Multiplayer/social interactions.
- Unit testing and refactoring into services/models.

## 👥 Author & Contributors

<table border="0" cellspacing="10" cellpadding="5">
  <tr>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/Jess2Jes">
        <img src="https://github.com/Jess2Jes.png" width="100" height="100" alt="Jess2Jes" style="border-radius: 50%;"/>
      </a>
      <br/>
      <a href="https://github.com/Jess2Jes">Jess2Jes</a>
    </td>
 <td align="center" style="border: 1px solid #555; padding: 10px;">
   <a href="https://github.com/Dendroculus">
     <img src="https://github.com/Dendroculus.png" width="100" height="100" alt="Hans" style="border-radius: 50%;"/>
   </a>
   <br/>
   <a href="https://github.com/Dendroculus">Hans</a>
 </td>

 <td align="center" style="border: 1px solid #555; padding: 10px;">
   <a href="https://github.com/StevNard">
     <img src="https://github.com/StevNard.png" width="100" height="100" alt="StevNard"/>
   </a>
   <br/>
   <a href="https://github.com/StevNard">StevNard</a>
 </td>
  </tr>
</table>

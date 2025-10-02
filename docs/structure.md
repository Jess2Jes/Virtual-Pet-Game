# 📝 Project Documentation – Virtual Pet Game
This document explains the internal structure and logic of the Virtual Pet Game.

## 📂 File breakdown

- **main.py**  
  Entry point of the program. Handles menus, session state, and integrates core modules (`game.py`, `shop.py`, `user.py`).

- **game.py**  
  Core gameplay loop.  
  Responsibilities:
  - 🐾 Pet selection
  - 🎮 Main interaction menu (feed, play, bathe, walk, sleep, talk, potions)
  - 📊 Status updates
  - ⏰ Time progression

- **pet.py**  
  `VirtualPet` class:
  - ❤️ Stores stats (happiness, hunger, sanity, health, fat, energy)
  - ⏳ Aging and life stage progression
  - 🛒 Shared stock lists for food, soap, and potions
  - 🐱 Behavior methods: `feed()`, `bathe()`, `sleep()`, `health_care()`, etc.

- **animal.py**  
  Subclasses for each pet type: Cat, Rabbit, Dinosaur, Dragon, Pou  
  - 🍗 Defines favorite foods
  - 🎨 ASCII art per life stage

- **formatter.py**  
  - ✂️ `truncate(text, max_len)` – line length limiter  
  - 📦 `format_status_box(stats)` – dynamic CLI status box

- **shop.py**  
  - 🛍️ Item catalog for food, soap, and potions
  - 💰 `buy()` method that deducts currency and updates stock

- **user.py**  
  - 🔑 User registration and authentication
  - ✅ Enforces password policy
  - 🐾 Tracks pets owned and user currency

## 💰 Shop & Economy
- 🍖 **Food**: affects hunger and happiness  
- 🧼 **Soap**: affects sanity and happiness  
- 🧪 **Potions**: various effects (energy, health, fat reduction, age advancement)  
- 📦 Each item has a stock count shared across all users

## 📝 Notes
- ⚖️ Stats are clamped 0–100 using `limit_stat()`  
- ⏳ Aging is handled by `time_past()` which reduces stats and updates life stage  
- 🎲 Randomness is applied for initial stats and walk events  
- 🛠️ Designed with extensibility for GUI, persistence, and additional animals

For gameplay instructions, refer to the [README](../README.md)

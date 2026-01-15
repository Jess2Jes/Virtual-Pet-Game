"""
constants/configs.py

Centralized configuration for game constants, assets, and rules.
Organized into classes for better maintainability and namespaces.
"""

import operator


class UIConfig:
    """General UI formatting and system messages."""
    LINE = "─" * 120
    GRID_LINE = '+-------+-------+-------+'
    NO_STOCK_MSG = "OUT OF STOCK"
    MAX_LENGTH = 0


class AuthConfig:
    """Authentication and Security constants."""
    USERNAME_INPUTTING = "Username: "
    PASSWORD_INPUTTING = "Password: "
    VALID_PASSWORD = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"


class MinigameConfig:
    """Registry for available minigames and their dynamic imports."""
    GAME_LIST = [
        "Math Quiz", "Tic Tac Toe", "Memory Match",
        "Battle Contest", "Sudoku", "Tetris", "Uno"
    ]

    SPECS = {
        "Math Quiz": {"module": "minigame.math_quiz", "class": "MathQuiz"},
        "Tic Tac Toe": {"module": "minigame.tic_tac_toe", "class": "TicTacToe"},
        "Memory Match": {"module": "minigame.memory_match", "class": "MemoryMatch"},
        "Battle Contest": {"module": "minigame.battle_contest", "class": "BattleContest"},
        "Sudoku": {"module": "minigame.sudoku", "class": "Sudoku"},
        "Tetris": {"module": "minigame.tetris", "class": "Tetris"},
        "Uno": {"module": "minigame.uno", "class": "Uno"},
    }


class PlayConfig:
    """Configuration for the 'Play' action."""
    # Costs & Rewards
    ENERGY_COST = 10
    HUNGER_COST = 30
    HEALTH_REQ = 20
    HAPPINESS_GAIN = 10
    HUNGER_DECREASE = 5
    ENERGY_DECREASE = 5
    MONEY_REWARD = 25000

    # Assets
    FLAVOR_TEXT = {
        "cat": "You play laser with",
        "rabbit": "You play catch ball with",
        "dinosaur": "You play hide and seek with",
        "dragon": "You play fireball with",
        "pou": "You brought to swimming pool",
        "default": "You play with",
    }

    EMOJIS = {
        "cat": "💥",
        "rabbit": "🤾",
        "dinosaur": "🏃",
        "dragon": "☄️",
        "pou": "🏊‍♂️",
        "default": "🎲",
    }


class WalkConfig:
    """Configuration for the 'Walk' action."""
    # Requirements
    ENERGY_REQ = 10
    HUNGER_REQ = 30
    HEALTH_REQ = 20
    
    # Costs & Rewards
    HAPPINESS_GAIN = 25
    HUNGER_COST = 5
    ENERGY_COST = 15
    LOST_MONEY = 100000
    FOUND_MONEY = 25000
    
    # Events
    MUD_SANITY_LOSS = 10
    ROTTEN_HEALTH_LOSS = 15


class FoodConfig:
    """Food items database and mapping."""
    DEFINITIONS = {
        "Kentucky Fried Chicken": {"emoji": "🍗", "hunger": 15, "happiness": 5, "price": 20000},
        "Ice Cream": {"emoji": "🍦", "hunger": 5, "happiness": 3, "price": 5000},
        "Fried Rice": {"emoji": "🥘", "hunger": 10, "happiness": 0, "price": 1000},
        "Salad": {"emoji": "🥗", "hunger": 10, "happiness": -5, "price": 5500},
        "French Fries": {"emoji": "🍟", "hunger": 5, "happiness": 5, "price": 30000},
        "Mashed Potato": {"emoji": "🥔", "hunger": 5, "happiness": -2, "price": 15000},
        "Mozarella Nugget": {"emoji": "🧀", "hunger": 20, "happiness": 10, "price": 25000},
    }

    CHOICE_MAP = {
        "1": "Kentucky Fried Chicken",
        "2": "Ice Cream",
        "3": "Fried Rice",
        "4": "Salad",
        "5": "French Fries",
        "6": "Mashed Potato",
        "7": "Mozarella Nugget",
    }


class SoapConfig:
    """Soap items database and mapping."""
    DEFINITIONS = {
        "Rainbow Bubble Soap": {"emoji": "🌈", "sanity": 50, "happiness": 20, "price": 55000},
        "Pink Bubble Soap": {"emoji": "💗", "sanity": 20, "happiness": 10, "price": 35000},
        "White Silk Soap": {"emoji": "⚪", "sanity": 10, "happiness": 5, "price": 10000},
        "Flower Bubble Soap": {"emoji": "🌸", "sanity": 30, "happiness": 15, "price": 25000},
    }

    CHOICE_MAP = {
        "1": "Rainbow Bubble Soap",
        "2": "Pink Bubble Soap",
        "3": "White Silk Soap",
        "4": "Flower Bubble Soap",
    }


class PotionConfig:
    """Potion items database, mapping, and identifiers."""
    # Identifiers
    FAT_BURNER = "Fat Burner"
    HEALTH_POTION = "Health Potion"
    ENERGIZER = "Energizer"
    ADULT_POTION = "Adult Potion"

    DEFINITIONS = {
        FAT_BURNER: {"emoji": "🧪", "type": "fat", "delta": -50, "price": 110000},
        HEALTH_POTION: {"emoji": "💊", "type": "health", "delta": 50, "price": 200000},
        ENERGIZER: {"emoji": "⚡", "type": "energy", "delta": 50, "price": 800000},
        ADULT_POTION: {"emoji": "💉", "type": "age", "delta": 20, "price": 1000000},
    }

    CHOICE_MAP = {
        "1": FAT_BURNER,
        "2": HEALTH_POTION,
        "3": ENERGIZER,
        "4": ADULT_POTION,
    }


class MathConfig:
    """Configuration for math-related minigames."""
    OPERATIONS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": lambda a, b: a // b if b != 0 else 0,
        "%": operator.mod,
        "**": operator.pow
    }


class UnoConstants:
    """Constants specifically for the Uno minigame."""
    COLORS = ['RED', 'YELLOW', 'GREEN', 'BLUE']
    VALUES = [str(num) for num in range(0, 10)]
    ACTION_CARDS = ['Skip', 'Reverse', 'DrawTwo']
    WILD_CARDS = ['Wild ColourChanger', 'Wild DrawFour']
    
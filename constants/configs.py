import operator

LINE = "─" * 120
GRID_LINE = '+-------+-------+-------+'
NO_STOCK = "OUT OF STOCK"
MAX_LENGTH = 0
USERNAME_INPUTTING = "Username: "
PASSWORD_INPUTTING = "Password: "
VALID_PASSWORD = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"

GAME_LIST = ["Math Quiz", "Tic Tac Toe", "Memory Match", 
            "Battle Contest", "Sudoku", "Tetris", "Uno"]

FAT_BURNER = "Fat Burner"
HEALTH_POTION = "Health Potion"
ENERGIZER = "Energizer"
ADULT_POTION = "Adult Potion"

FOOD_DEF = {
        "Kentucky Fried Chicken": {"emoji": "🍗", "hunger": 15, "happiness": 5, "price": 20000},
        "Ice Cream": {"emoji": "🍦", "hunger": 5, "happiness": 3, "price": 5000},
        "Fried Rice": {"emoji": "🥘", "hunger": 10, "happiness": 0, "price": 1000},
        "Salad": {"emoji": "🥗", "hunger": 10, "happiness": -5, "price": 5500},
        "French Fries": {"emoji": "🍟", "hunger": 5, "happiness": 5, "price": 30000},
        "Mashed Potato": {"emoji": "🥔", "hunger": 5, "happiness": -2, "price": 15000},
        "Mozarella Nugget": {"emoji": "🧀", "hunger": 20, "happiness": 10, "price": 25000},
    }

SOAP_DEF = {
        "Rainbow Bubble Soap": {"emoji": "🌈", "sanity": 50, "happiness": 20, "price": 55000},
        "Pink Bubble Soap": {"emoji": "💗", "sanity": 20, "happiness": 10, "price": 35000},
        "White Silk Soap": {"emoji": "⚪", "sanity": 10, "happiness": 5, "price": 10000},
        "Flower Bubble Soap": {"emoji": "🌸", "sanity": 30, "happiness": 15, "price": 25000},
    }

POTION_DEF = {
        FAT_BURNER: {"emoji": "🧪", "type": "fat", "delta": -50, "price": 110000},
        HEALTH_POTION: {"emoji": "💊", "type": "health", "delta": 50, "price": 200000},
        ENERGIZER: {"emoji": "⚡", "type": "energy", "delta": 50, "price": 800000},
        ADULT_POTION: {"emoji": "💉", "type": "age", "delta": 20, "price": 1000000},
    }

ARITHMETIC_OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": lambda a, b: a // b if b != 0 else 0,
    "%": operator.mod,
    "**": operator.pow
}

class UnoConstants:
    COLORS = ['RED', 'YELLOW', 'GREEN', 'BLUE']
    VALUES = [str(num) for num in range(0, 10)]
    ACTION_CARDS = ['Skip', 'Reverse', 'DrawTwo']
    WILD_CARDS = ['Wild ColourChanger', 'Wild DrawFour']
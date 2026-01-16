from typing import List, Tuple
import asyncio
from utils.formatter import clear
from utils.loading import loading_bar
from .user import User
from constants.configs import (
    UIConfig as UIC, 
    FoodConfig as FC, 
    SoapConfig as SC, 
    PotionConfig as PC
    )
from utils.colorize import red, green
from utils.ports import OutputPort, InputPort, ConsoleIO

"""
shop.py

Console-driven Shop UI for the Virtual Pet Game.

Responsibilities:
- Present catalogs for food, soap, and potion items.
- Allow the player to purchase items (checks currency and updates inventory).
- Show the player's current currency.
- Provide a simple interactive loop (interact) used by the higher-level game flows.

Notes:
- The Shop expects a User instance with attributes: currency, inventory, add_item, limit_currency.
- All behavior is preserved; this update only adds documentation and small clarifying comments.
"""

class Shop:
    """
    Shopping assistant for a specific user.

    The Shop instance is constructed with a User object and operates on that user's
    currency and inventory.
    """
    def __init__(self, user: User, io: InputPort | OutputPort = None):
        """
        Args:
            user: the User instance who is shopping.
        """
        self.user = user
        self.io = io or ConsoleIO()

    def _input_int(self, prompt: str):
        """
        Read an integer from stdin and return it; return None on invalid input.

        This central helper keeps input parsing consistent across the shop UI.
        """
        try:
            return int(self.io.read(prompt))
        except ValueError:
            return None

    def show_currency(self) -> None:
        """self.io.write the user's current currency with a small friendly message."""
        self.io.write(UIC.LINE)
        money = self.user.currency
        if money >= 1000:
            self.io.write(f"🐼 : Your current currency: Rp. {'{:,}'.format(money)}")
        else:
            self.io.write(f"🐼 : Your current currency: Rp. {money}")
        self.io.write(red("🐼 : You are broke... 💸") if money < 5000 else green("🐼 : You still have lots... 💰"))
        self.io.write(UIC.LINE + "\n")
        
    def _list_items(self, category: str, definition: dict) -> List[Tuple[str, str, int, int, int]]:
        """
        Return a list of tuples describing available items in the given category.
        
        Args:
            category: The internal category key (e.g., "food").
            definition: The item definition dictionary for the category.
        
        Returns : 
            A list of tuples (name, emoji, price, qty, index) for each item.
        """
        inv = self.user.inventory[category]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(definition.items(), start=1):
            emoji = data["emoji"]
            price = int(data["price"])
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items
    
    def catalog_items(self, title: str, category: str, item_def) -> None:
        """
        self.io.write the formatted catalog for the given category to the console.
        
        Args:
            title: The display title for the category (e.g., "FOOD").
            category: The internal category key (e.g., "food").
            item_def: The item definition dictionary for the category.
        
        Returns:
            None
        """
        self.io.write(UIC.LINE)
        self.io.write(f"{title} CATALOG")
        self.io.write(UIC.LINE)
        for name, emoji, price, qty, i in self._list_items(category, item_def):
            stock_text = f"{qty}" if qty > 0 else f"0 ({UIC.NO_STOCK_MSG})"
            self.io.write(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        self.io.write(UIC.LINE + "\n")

    def _buy_category_and_index(self) -> tuple[str | None, int | None]:
        """
        Interactively ask the user which category they want to buy from and return
        the category key plus the selected item index (1-based). Returns (None, None)
        on invalid selection.
        """
        self.io.write(UIC.LINE)
        self.io.write("🐼 : Hello, my lovely customer, welcome to our store!")
        self.io.write("\n🐼 : What do you want to buy?")
        self.io.write(UIC.LINE)
        self.io.write("1. Food")
        self.io.write("2. Soap")
        self.io.write("3. Potion")
        self.io.write(UIC.LINE)
        cat = self._input_int("🐼 : Choose category (1-3): ")
        if cat not in (1, 2, 3):
            self.io.write(red("\n🐼 : Please choose between 1-3 please..."))
            return None, None

        self.io.write(UIC.LINE)

        if cat == 1:
            self.catalog_items("FOOD", "food", FC.DEFINITIONS)
            idx = self._input_int("🐼 : Choose food number: ")
            return "food", idx
        elif cat == 2:
            self.catalog_items("SOAP", "soap", SC.DEFINITIONS)
            idx = self._input_int("🐼 : Choose soap number: ")
            return "soap", idx
        else:
            self.catalog_items("POTION", "potion", PC.DEFINITIONS)
            idx = self._input_int("🐼 : Choose potion number: ")
            return "potion", idx

    def _resolve_item_by_index(self, category: str, idx: int) -> str | None:
        """
        Resolve the item name by the user-visible index within the chosen category.

        Returns None on invalid index.
        """
        if idx is None:
            return None

        if category == "food":
            items = self._list_items("food", FC.DEFINITIONS)
        elif category == "soap":
            items = self._list_items("soap", SC.DEFINITIONS)
        else:
            items = self._list_items("potion", PC.DEFINITIONS)
            
        if not (1 <= idx <= len(items)):
            self.io.write(red("\n🐼 : Invalid item number."))
            return None

        return items[idx - 1][0]

    def _price_for_category(self, category: str, name: str) -> int:
        """Return the price of a named item for the given category."""
        if category == "food":
            return int(FC.DEFINITIONS[name]["price"])
        elif category == "soap":
            return int(SC.DEFINITIONS[name]["price"])
        else:
            return int(PC.DEFINITIONS[name]["price"])

    def _add_stock(self, category: str, name: str, amount: int) -> None:
        """Add amount of item to the user's inventory via the User API."""
        self.user.add_item(category, name, amount)

    def _buy_flow(self) -> None:
        """
        Complete purchase flow:
         - choose category and item
         - ask quantity
         - verify affordability
         - deduct currency and add to inventory
        """
        category, idx = self._buy_category_and_index()
        if category is None or idx is None:
            return
        name = self._resolve_item_by_index(category, idx)
        if not name:
            return

        while True:
            amount = self._input_int("🐼 : How many do you want to buy? ")
            if amount is None or amount <= 0:
                self.io.write(red("\n🐼 : Please input a positive number!"))
                continue
            break

        price_per = self._price_for_category(category, name)
        total = price_per * amount

        if total > self.user.currency:
            self.io.write(red(f"\n🐼 : Not enough amount to buy {name}!"))
            self.io.write(f"🐼 : Needed: Rp. {'{:,}'.format(total)}, You have: Rp. {'{:,}'.format(self.user.currency)}\n")
            return

        # Deduct currency and add items to inventory
        self.user.currency = self.user.currency - total
        self.user.limit_currency()
        self._add_stock(category, name, amount)

        if category == "food":
            emoji = FC.DEFINITIONS[name]["emoji"]
        elif category == "soap":
            emoji = SC.DEFINITIONS[name]["emoji"]
        else:
            emoji = PC.DEFINITIONS[name]["emoji"]
        emoji = str(emoji)

        self.io.write(f"\n🐼 : You bought {amount} {name} {emoji}! Fantastic!")
        new_qty = self.user.inventory[category][name]
        self.io.write(f"\n🐼 : Your current {name} {emoji} : {new_qty}")

        money_left = self.user.currency
        if money_left >= 1000:
            self.io.write(f"🐼 : Total money left: Rp. {'{:,}'.format(money_left)}\n")
        else:
            self.io.write(f"🐼 : Total money left: Rp. {money_left}\n")

    def interact(self) -> None:
        """
        Top-level shop interaction loop displayed to the user.

        Options:
         1 - Buy Item
         2 - Show Current Currency
         3 - Exit
        """
        self.io.write("\n🐼 : Hi, I'm Po Ping. I'll be your shopping assistant for today!")
        asyncio.run(loading_bar())
        clear()
        while True:
            self.io.write("\n🐼 : Here's list of options you can do!")
            # There will also be a sell item menu in here soon!
            # You can also try to bargain here in the future updates!
            self.io.write('='*120)
            self.io.write("1. Buy Item")
            self.io.write("2. Show Current Currency")
            self.io.write("3. Exit")
            self.io.write('='*120)

            choice = self._input_int("🐼 : Choose (1-3): ")
            if choice is None:
                self.io.write(red("\n🐼 : Please insert digit in choice input!"))
                continue

            actions = {
                1: self._buy_flow,
                2: self.show_currency
            }

            if choice == 3:
                self.io.write("\n🐼 : Thank you for shopping. Wish you well!\n")
                break

            action = actions.get(choice)
            if action:
                self.io.write("")
                action()
            else:
                self.io.write(red("\n🐼 : Please choose between 1-3 please..."))
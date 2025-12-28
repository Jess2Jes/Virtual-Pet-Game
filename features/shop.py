from typing import List, Tuple
import asyncio
from colorama import init

from utils.formatter import clear
from utils.loading import loading_bar
from .user import User
from constants.configs import LINE, SOAP_DEF, FOOD_DEF, POTION_DEF, NO_STOCK
from utils.colorize import red, green

init(autoreset=True)



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
    def __init__(self, user: User):
        """
        Args:
            user: the User instance who is shopping.
        """
        self.user = user

    @staticmethod
    def _input_int(prompt: str):
        """
        Read an integer from stdin and return it; return None on invalid input.

        This central helper keeps input parsing consistent across the shop UI.
        """
        try:
            return int(input(prompt))
        except ValueError:
            return None

    def show_currency(self) -> None:
        """Print the user's current currency with a small friendly message."""
        print(LINE)
        money = self.user.currency
        if money >= 1000:
            print(f"🐼 : Your current currency: Rp. {'{:,}'.format(money)}")
        else:
            print(f"🐼 : Your current currency: Rp. {money}")
        print(red("🐼 : You are broke... 💸") if money < 5000 else green("🐼 : You still have lots... 💰"))
        print(LINE + "\n")

    def _list_food_items(self) -> List[Tuple[str, str, int, int, int]]:
        """Return a list of tuples describing available food items (name, emoji, price, qty, index)."""
        inv = self.user.inventory["food"]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(FOOD_DEF.items(), start=1):
            emoji = data["emoji"]
            price = int(data["price"])
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items

    def _list_soap_items(self) -> List[Tuple[str, str, int, int, int]]:
        """Return a list of soap items (name, emoji, price, qty, index)."""
        inv = self.user.inventory["soap"]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(SOAP_DEF.items(), start=1):
            emoji = data["emoji"]
            price = int(data["price"])
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items

    def _list_potion_items(self) -> List[Tuple[str, str, int, int, int]]:
        """Return a list of potion items (name, emoji, price, qty, index)."""
        inv = self.user.inventory["potion"]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(POTION_DEF.items(), start=1):
            emoji = data["emoji"]
            price = int(data["price"])
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items

    def catalog_food(self) -> None:
        """Print the formatted food catalog to the console."""
        print(LINE)
        print("FOOD CATALOG")
        print(LINE)
        for name, emoji, price, qty, i in self._list_food_items():
            stock_text = f"{qty}" if qty > 0 else f"0 ({NO_STOCK})"
            print(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        print(LINE + "\n")

    def catalog_soap(self) -> None:
        """Print the formatted soap catalog to the console."""
        print(LINE)
        print("SOAP CATALOG")
        print(LINE)
        for name, emoji, price, qty, i in self._list_soap_items():
            stock_text = f"{qty}" if qty > 0 else f"0 ({NO_STOCK})"
            print(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        print(LINE + "\n")

    def catalog_potion(self) -> None:
        """Print the formatted potion catalog to the console."""
        print(LINE)
        print("POTION CATALOG")
        print(LINE)
        for name, emoji, price, qty, i in self._list_potion_items():
            stock_text = f"{qty}" if qty > 0 else f"0 ({NO_STOCK})"
            print(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        print(LINE + "\n")

    def _buy_category_and_index(self) -> tuple[str | None, int | None]:
        """
        Interactively ask the user which category they want to buy from and return
        the category key plus the selected item index (1-based). Returns (None, None)
        on invalid selection.
        """
        print(LINE)
        print("🐼 : Hello, my lovely customer, welcome to our store!")
        asyncio.run(loading_bar())
        print("\n🐼 : What do you want to buy?")
        print(LINE)
        print("1. Food")
        print("2. Soap")
        print("3. Potion")
        print(LINE)
        cat = self._input_int("🐼 : Choose category (1-3): ")
        if cat not in (1, 2, 3):
            print(red("\n🐼 : Please choose between 1-3 please..."))
            return None, None

        print()

        if cat == 1:
            self.catalog_food()
            idx = self._input_int("🐼 : Choose food number: ")
            return "food", idx
        elif cat == 2:
            self.catalog_soap()
            idx = self._input_int("🐼 : Choose soap number: ")
            return "soap", idx
        else:
            self.catalog_potion()
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
            items = self._list_food_items()
        elif category == "soap":
            items = self._list_soap_items()
        else:
            items = self._list_potion_items()

        if not (1 <= idx <= len(items)):
            print(red("\n🐼 : Invalid item number."))
            return None

        return items[idx - 1][0]

    def _price_for_category(self, category: str, name: str) -> int:
        """Return the price of a named item for the given category."""
        if category == "food":
            return int(FOOD_DEF[name]["price"])
        elif category == "soap":
            return int(SOAP_DEF[name]["price"])
        else:
            return int(POTION_DEF[name]["price"])

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
                print(red("\n🐼 : Please input a positive number!"))
                continue
            break

        price_per = self._price_for_category(category, name)
        total = price_per * amount

        if total > self.user.currency:
            print(red(f"\n🐼 : Not enough amount to buy {name}!"))
            print(f"🐼 : Needed: Rp. {'{:,}'.format(total)}, You have: Rp. {'{:,}'.format(self.user.currency)}\n")
            return

        # Deduct currency and add items to inventory
        self.user.currency = self.user.currency - total
        self.user.limit_currency()
        self._add_stock(category, name, amount)

        if category == "food":
            emoji = FOOD_DEF[name]["emoji"]
        elif category == "soap":
            emoji = SOAP_DEF[name]["emoji"]
        else:
            emoji = POTION_DEF[name]["emoji"]
        emoji = str(emoji)

        print(f"\n🐼 : You bought {amount} {name} {emoji}! Fantastic!")
        new_qty = self.user.inventory[category][name]
        print(f"\n🐼 : Your current {name} {emoji} : {new_qty}")

        money_left = self.user.currency
        if money_left >= 1000:
            print(f"🐼 : Total money left: Rp. {'{:,}'.format(money_left)}\n")
        else:
            print(f"🐼 : Total money left: Rp. {money_left}\n")

    def interact(self) -> None:
        """
        Top-level shop interaction loop displayed to the user.

        Options:
         1 - Buy Item
         2 - Show Current Currency
         3 - Exit
        """
        print("\n🐼 : Hi, I'm Po Ping. I'll be your shopping assistant for today!")
        asyncio.run(loading_bar())
        clear()
        while True:
            print("\n🐼 : Here's list of options you can do!")
            # There will also be a sell item menu in here soon!
            # You can also try to bargain here in the future updates!
            print('='*120)
            print("1. Buy Item")
            print("2. Show Current Currency")
            print("3. Exit")
            print('='*120)

            choice = self._input_int("🐼 : Choose (1-3): ")
            if choice is None:
                print(red("\n🐼 : Please insert digit in choice input!"))
                continue

            actions = {
                1: self._buy_flow,
                2: self.show_currency
            }

            if choice == 3:
                print("\n🐼 : Thank you for shopping. Wish you well!\n")
                break

            action = actions.get(choice)
            if action:
                print()
                action()
            else:
                print(red("\n🐼 : Please choose between 1-3 please..."))
from .pet import VirtualPet
from typing import List, Tuple
from .formatter import GARIS
from .user import User
import time
from colorama import Fore, init
init(autoreset=True)

OUT_OF_STOCK = "Out of Stock"

class Shop:
    def __init__(self, user: User):
        self.user = user

    @staticmethod
    def _input_int(prompt: str):
        try:
            return int(input(prompt))
        except ValueError:
            return None

    def show_currency(self) -> None:
        print(GARIS)
        money = self.user.currency
        if money >= 1000:
            print(f"🐼 : Your current currency: Rp. {'{:,}'.format(money)}")
        else:
            print(f"🐼 : Your current currency: Rp. {money}")
        print("🐼 : You are broke... 💸" if money < 5000 else "🐼 : You still have lots... 💰")
        print(GARIS + "\n")

    def _list_food_items(self) -> List[Tuple[str, str, int, int, int]]:
        inv = self.user.inventory["food"]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(VirtualPet.FOOD_DEF.items(), start=1):
            emoji = data["emoji"]  
            price = int(data["price"])  
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items

    def _list_soap_items(self) -> List[Tuple[str, str, int, int, int]]:
        inv = self.user.inventory["soap"]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(VirtualPet.SOAP_DEF.items(), start=1):
            emoji = data["emoji"]  
            price = int(data["price"])  
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items

    def _list_potion_items(self) -> List[Tuple[str, str, int, int, int]]:
        inv = self.user.inventory["potion"]
        items: List[Tuple[str, str, int, int, int]] = []
        for i, (name, data) in enumerate(VirtualPet.POTION_DEF.items(), start=1):
            emoji = data["emoji"]  
            price = int(data["price"])  
            qty = inv.get(name, 0)
            items.append((name, emoji, price, qty, i))
        return items

    def catalog_food(self) -> None:
        print(GARIS)
        print("FOOD CATALOG")
        print(GARIS)
        for name, emoji, price, qty, i in self._list_food_items():
            stock_text = f"{qty}" if qty > 0 else f"0 ({OUT_OF_STOCK})"
            print(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        print(GARIS + "\n")

    def catalog_soap(self) -> None:
        print(GARIS)
        print("SOAP CATALOG")
        print(GARIS)
        for name, emoji, price, qty, i in self._list_soap_items():
            stock_text = f"{qty}" if qty > 0 else f"0 ({OUT_OF_STOCK})"
            print(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        print(GARIS + "\n")

    def catalog_potion(self) -> None:
        print(GARIS)
        print("POTION CATALOG")
        print(GARIS)
        for name, emoji, price, qty, i in self._list_potion_items():
            stock_text = f"{qty}" if qty > 0 else f"0 ({OUT_OF_STOCK})"
            print(f"{i}. {name} {emoji} - Rp. {'{:,}'.format(price)} | Stock: {stock_text}")
        print(GARIS + "\n")

    def _buy_category_and_index(self) -> tuple[str | None, int | None]:
        print(GARIS)
        print("🐼 : Hello, my lovely customer, welcome to our store!")
        time.sleep(0.5)
        print("\n🐼 : What do you want to buy?")
        print(GARIS)
        print("1. Food")
        print("2. Soap")
        print("3. Potion")
        print(GARIS)
        cat = self._input_int("🐼 : Choose category (1-3): ")
        if cat not in (1, 2, 3):
            print("\n🐼 : Please choose between 1-3 please...")
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
        if idx is None:
            return None
        
        if (category == "food"):
            items = self._list_food_items()
        elif (category == "soap"):
            items = self._list_soap_items()
        else:
            items = self._list_potion_items()

        if not (1 <= idx <= len(items)):
            print("\n🐼 : Invalid item number.")
            return None
        return items[idx - 1][0]

    def _price_for_category(self, category: str, name: str) -> int:
        if category == "food":
            return int(VirtualPet.FOOD_DEF[name]["price"])
        elif category == "soap":
            return int(VirtualPet.SOAP_DEF[name]["price"])
        else:
            return int(VirtualPet.POTION_DEF[name]["price"])

    def _add_stock(self, category: str, name: str, amount: int) -> None:
        self.user.add_item(category, name, amount)

    def _buy_flow(self) -> None:
        category, idx = self._buy_category_and_index()
        if category is None or idx is None:
            return
        name = self._resolve_item_by_index(category, idx)
        if not name:
            return

        while True:
            amount = self._input_int("🐼 : How many do you want to buy? ")
            if amount is None or amount <= 0:
                print("\n🐼 : Please input a positive number!")
                continue
            break

        price_per = self._price_for_category(category, name)
        total = price_per * amount

        if total > self.user.currency:
            print(f"\n🐼 : Not enough amount to buy {name}!")
            print(f"🐼 : Needed: Rp. {'{:,}'.format(total)}, You have: Rp. {'{:,}'.format(self.user.currency)}\n")
            return

        self.user.currency = self.user.currency - total
        self.user.limit_currency()
        self._add_stock(category, name, amount)

        emoji = (
            VirtualPet.FOOD_DEF[name]["emoji"] if category == "food"
            else VirtualPet.SOAP_DEF[name]["emoji"] if category == "soap"
            else VirtualPet.POTION_DEF[name]["emoji"]
        )
        emoji = str(emoji)

        print(f"\n🐼 : You bought {amount} {name} {emoji}! Fantastic!")
        new_qty = self.user.inventory[category][name]
        print(f"\n🐼 : Your current {name} {emoji}'s {new_qty}")

        money_left = self.user.currency
        if money_left >= 1000:
            print(f"🐼 : Total money left: Rp. {'{:,}'.format(money_left)}\n")
        else:
            print(f"🐼 : Total money left: Rp. {money_left}\n")

    def interact(self) -> None:
        print("\n🐼 : Hi, I'm Po Ping. I'll be your shopping assistant for today!")
        time.sleep(0.5)
        while True:
            print("\n🐼 : Here's list of options you can do!")
            # There will also be a sell item menu in here soon!
            # You can also try to bargain here in the future updates!
            print('='*101)
            print("1. Buy Item")
            print("2. Show Current Currency")
            print("3. Exit")
            print('='*101)

            choice = self._input_int("🐼 : Choose (1-3): ")
            if choice is None:
                print("\n🐼 : Please insert digit in choice input!")
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
                print("\n🐼 : Please choose between 1-3 please...")
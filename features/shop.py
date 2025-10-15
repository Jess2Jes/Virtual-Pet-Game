from .pet import VirtualPet
from typing import Dict
from .formatter import GARIS

class Shop:

    food: Dict[str, int] = {
        "Kentucky Fried Chicken": 20000,
        "Ice Cream": 5000,
        "Fried Rice": 1000,
        "Salad": 5500,
        "French Fries": 30000,
        "Mashed Potato": 15000,
        "Mozarella Nugget": 25000

    }

    soap: Dict[str, int] = {
        "Rainbow Bubble Soap": 55000,
        "Pink Bubble Soap": 35000,
        "White Silk Soap": 10000
    }

    potion: Dict[str, int] = {
        "Fat Burner": 110000,
        "Health Potion": 200000,
        "Energizer": 800000,
        "Adult Potion": 1000000
    }

    def __init__(self, user):
        self.user = user
        self.money = user.current_user.currency

    @staticmethod
    def _input_int(prompt: str):
        try:
            return int(input(prompt))
        except ValueError:
            return None

    def show_currency(self) -> None:
        print(GARIS)

        if (self.money >= 1000):
            print(f"Your current currency: Rp. {"{:,}".format(self.money)}")
        else:
            print(f"Your current currency: Rp. {self.money}")

        if (self.money < 5000):
            print("You are broke... 💸")
        else:
            print("You still have lots... 💰")
        print(GARIS + "\n")
    
    def catalog_food(self) -> None:
        print(GARIS)
        for key, value in self.food.items():
            print(f"-> {key} : {"{:,}".format(value)}")
        print(GARIS + "\n")
        print(GARIS)
        print("Your Current Food Stock:")
        print(GARIS)
        for key, value in VirtualPet.list_food.items():
            print(f"-> {key} : {value[0]}")
        print(GARIS + "\n")

    def catalog_soap(self) -> None:
        print(GARIS)
        for key, value in self.soap.items():
            print(f"-> {key} : {"{:,}".format(value)}")
        print(GARIS + "\n")
        print(GARIS)
        print("Your Current Soap Stock:")
        print(GARIS)
        for key, value in VirtualPet.list_soap.items():
            print(f"-> {key} : {value[0]}")
        print(GARIS + "\n")
    
    def catalog_potion(self) -> None:
        print(GARIS)
        for key, value in self.potion.items():
            print(f"-> {key} : Rp. {"{:,}".format(value)}")
        print(GARIS + "\n")
        print(GARIS)
        print("Your Current Potion Stock:")
        print(GARIS)
        for key, value in VirtualPet.list_potion.items():
            print(f"-> {key} : {value[0]}")
        print(GARIS + "\n")
    
    def buy(self, item, amount) -> None:
        if (not ((item in self.food.keys()) or (item in self.soap.keys()) 
            or (item in self.potion.keys()))):

            print(f"\nThere's currently no {item} in this shop.\n")
            return

        if (self.money == 0):
            print("\nYou cannot buy anything anymore!\n")
            return
        
        print(f"\nYou bought {amount} {item}!\n")
        
        if (item in self.food.keys()):
            if (self.food[item] * amount > self.money):
                print(f"Not enough amount to buy {item}!\n")
                return
            self.user.currency -= (self.food[item] * amount)
            self.money = self.user.currency
            VirtualPet.list_food[item][0] += amount
            print(f"\nYour current {item} has: {VirtualPet.list_food[item][0]}")
        
        elif (item in self.soap.keys()):
            if (self.soap[item] * amount > self.money):
                print(f"Not enough amount to buy {item}!\n")
                return
            self.user.currency -= (self.soap[item] * amount)
            self.money = self.user.currency
            VirtualPet.list_soap[item][0] += amount
            print(f"\nYour current {item} has: {VirtualPet.list_soap[item][0]}")
        
        elif (item in self.potion.keys()):
            if (self.potion[item] * amount > self.money):
                print(f"Not enough amount to buy {item}!\n")
                return
            self.user.currency -= (self.potion[item] * amount)
            self.money = self.user.currency
            VirtualPet.list_potion[item][0] += amount
            print(f"\nYour current {item} has: {VirtualPet.list_potion[item][0]}")
        
        if (self.money < 0):
            self.money = 0

        if (self.money >= 1000):
            print(f"Total money left: Rp. {"{:,}".format(self.money)}\n")
        else:
            print(f"Total money left: Rp. {self.money}\n")

    def _buy_flow(self) -> None:
        item = input("What do you want to buy? ").title()
        while True:
            amount = self._input_int("How many do you want to buy? ")
            if amount is not None:
                break
            else:
                print("\nPlease input number in amount!")
        self.buy(item, amount)

    def interact(self) -> None:
        while True: 
            print("\n" + "="*40 + " " + "Welcome to Pet Shop" + " " + "="*40)  
            print("1. See Food Catalog")
            print("2. See Soap Catalog")
            print("3. See Potion Catalog")
            print("4. Buy Item")
            print("5. Show Current Currency")
            print("6. Exit")
            print('='*101)

            choice = self._input_int("Choose (1-6): ")
            if choice is None:
                print("\nPlease insert digit at choice input!")
                continue

            actions = {
                1: self.catalog_food,
                2: self.catalog_soap,
                3: self.catalog_potion,
                4: self._buy_flow,
                5: self.show_currency
            }

            if choice == 6:
                print("\nThank you for shopping.\n")
                break

            action = actions.get(choice)
            if action:
                print()
                action()
            else:
                print("\nPlease choose from (1-6).")
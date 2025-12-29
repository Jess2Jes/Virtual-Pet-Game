from .baseClass import MinigameStrategy
import time
from random import randint, choice
from utils.colorize import red, green
from constants.configs import LINE
from features.user import User
from typing import Any
from colorama import init

init(autoreset=True)

class BattleContest(MinigameStrategy):
    """Simple multi-round pet-battle simulation against another player's pet."""

    name = "Battle Tournament"

    def setup(self, player, pet):
        self.player = player
        self.player_pet = pet
        self.player_pet_stats = {
            "strength": 15,
            "agility": 10
        }
        self.current_round = 1
        self.player_health = self.player_pet.health * 1000
        self.player_won = 0
        other_players_with_pets = list(filter(lambda user: user != self.player and user.pets, User.users.values()))
        if other_players_with_pets:
            self.opponent = choice(other_players_with_pets)
            self.opponent_pet = choice(self.opponent.pets)
        else:
            print(red("\nOther players currently doesn't have any pets yet!\n"))
            return False
        self.opponent_health = self.opponent_pet.health * 1000
        self.opponent_won = 0
        self.opponent_pet_stats = {
            "strength": 25,
            "agility": 15
        }
        self.player_heal_count = 0
        self.player_heal_limit = 3
        self.opponent_heal_count = 0
        self.opponent_heal_limit = 5
        return True

    def display_menu(self):
        """Display battle status and available actions for the current round."""
        print("\n" + LINE)
        print(f"PET BATTLE TOURNAMENT -> ROUND - {self.current_round}".center(len(LINE)))
        print(LINE)
        print("\n" + LINE)
        print(f"Your Pet: {self.player_pet.name} {self.player_pet.emoji}")
        print(f"Health: {self.player_health}")
        print(f"Strength: {self.player_pet_stats['strength']}")
        print(f"Agility: {self.player_pet_stats['agility']}")
        print('-' * len(LINE))

        if self.opponent_pet:
            print(f"Opponent: {self.opponent_pet.name} {self.opponent_pet.emoji}")
            print(f"Health: {self.opponent_health}")
            print(f"Strength: {self.player_pet_stats['strength']}")
            print(f"Agility: {self.player_pet_stats['agility']}")

        print(LINE)
        print("\nBattle Options:")
        print(LINE)
        print("1. Attack 🗡️")
        print("2. Defend 🛡️")
        print("3. Special Move ✨")
        print("4. Heal ❤️‍🩹")
        print(LINE)

    def get_input(self):
        """Prompt and validate a numeric choice for the battle action."""
        while True:
            try:
                choice = int(input("Choose your action (1-4): "))
                if 1 <= choice <= 4:
                    return choice
                else:
                    print(red("Please enter a number between 1-4!"))
            except ValueError:
                print(red("Please enter a valid number!"))

    def build_question(self) -> Any:
        """Prepare the battle sequence and announce start."""
        print("\n" + LINE)
        print("Battle Starting!")
        print(LINE)
        print(f"{self.player_pet.name} {self.player_pet.emoji} VS {self.opponent_pet.name} {self.opponent_pet.emoji}")
        print("Prepare for battle!")
        time.sleep(2)

    def build_game(self) -> Any:
        """Main battle loop: alternate player/opponent actions until one health reaches 0."""
        while self.opponent_health > 0 and self.player_health > 0:
            self.display_menu()
            player_choice = self.get_input()

            self._execute_player_action(player_choice)
            self._execute_opponent_action()

            self.current_round += 1
            time.sleep(1)

        self._determine_battle_outcome()

        battle_result = {
            "player_health": max(0, self.player_health),
            "opponent_health": max(0, self.opponent_health),
            "player_won": (self.player_won > self.opponent_won),
            "rounds_played": self.current_round
        }

        return battle_result

    def _execute_player_action(self, choice: int) -> None:
        """Execute the player's chosen action."""
        if choice == 1:
            self._player_attack()
        elif choice == 2:
            self._player_defend()
        elif choice == 3:
            self._player_special_move()
        elif choice == 4:
            self._player_heal()

    def _execute_opponent_action(self) -> None:
        """Execute the opponent's action chosen at random."""
        opponent_choice = randint(1, 4)

        if opponent_choice == 1:
            self._opponent_attack()
        elif opponent_choice == 2:
            self._opponent_defend()
        elif opponent_choice == 3:
            self._opponent_special_move()
        elif opponent_choice == 4:
            self._opponent_heal()

    def _player_attack(self) -> None:
        """Player attacks the opponent."""
        damage = (randint(5, 10) + self.player_pet_stats["strength"] // 3) * 300
        self.opponent_health -= damage
        print(f"\n{self.player_pet.name} attacks for {damage} damage ⚔️!")

    def _player_defend(self) -> None:
        """Player defends, temporarily reducing incoming damage (display only)."""
        defense_bonus = randint(2, 5) * 3000
        print(f"\n{self.player_pet.name} defends 🛡️!")
        print(f"Damage reduction: {defense_bonus}")

    def _player_special_move(self) -> None:
        """Player uses special move (only on even rounds)."""
        if self.current_round % 2 == 0:
            special_damage = (randint(10, 15) + self.player_pet_stats["strength"] // 2) * 600
            self.opponent_health -= special_damage
            print(f"\n{self.player_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            print(red("\nSpecial moves are locked in odd rounds!"))

    def _player_heal(self) -> None:
        """Player heals if heal limit not exceeded."""
        if self.player_heal_count < self.player_heal_limit:
            heal_amount = randint(8, 12) * 500
            self.player_health += heal_amount
            print(f"\n{self.player_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.player_heal_count += 1
        else:
            print(red("\nYou already healed 3 times!"))

    def _opponent_attack(self) -> None:
        """Opponent attacks the player."""
        damage = (randint(4, 8) + self.opponent_pet_stats["strength"] // 3) * 300
        self.player_health -= damage
        print(f"{self.opponent_pet.name} attacks for {damage} damage ⚔️!")

    def _opponent_defend(self) -> None:
        """Opponent defends (display only)."""
        defense_bonus = randint(1, 4) * 3000
        print(f"{self.opponent_pet.name} defends 🛡️!")
        print(f"Damage reduction: {defense_bonus}")

    def _opponent_special_move(self) -> None:
        """Opponent special move (only on odd rounds)."""
        if self.current_round % 2 != 0:
            special_damage = (randint(8, 12) + self.opponent_pet_stats["strength"] // 2) * 600
            self.player_health -= special_damage
            print(f"{self.opponent_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            print(red("\nOpponent's special moves are restricted on even rounds!"))

    def _opponent_heal(self) -> None:
        """Opponent heals if heal limit not exceeded."""
        if self.opponent_heal_count < self.opponent_heal_limit:
            heal_amount = randint(6, 10) * 500
            self.opponent_health += heal_amount
            print(f"{self.opponent_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.opponent_heal_count += 1
        else:
            print(red("\nOpponent's healing ability are restricted to 5 times only!"))

    def _determine_battle_outcome(self) -> None:
        """Determine and display the battle outcome and update counters."""
        if self.opponent_health <= 0:
            print(f"{self.opponent_pet.name} was defeated 🎉!")
            self.player_won += 1
            self.current_round += 1

        if self.player_health <= 0:
            print(f"{self.player_pet.name} was defeated 🎉!")
            self.opponent_won += 1

        if self.player_health <= 0 and self.opponent_health <= 0:
            print("It's a draw! 🤺")

    def evaluate(self, answer):
        """Construct a richer evaluation dict from raw battle results."""
        battle_result = answer
        player_won = battle_result.get("player_won", False)
        player_health = battle_result.get("player_health", 0)
        opponent_health = battle_result.get("opponent_health", 0)

        evaluation = {
            "victory": player_won,
            "player_health_remaining": player_health,
            "opponent_health_remaining": opponent_health,
            "performance_score": min(100, (player_health * 3) + (50 if player_won else 0)),
            "battle_ended": (player_health <= 0 or opponent_health <= 0)
        }

        return evaluation

    def reward(self, result):
        """Compute and print battle rewards based on performance and outcome."""
        victory = bool(result.get("victory", False))
        performance_score = int(result.get("performance_score", 0))
        player_health_remaining = int(result.get("player_health_remaining", 0))

        coins = 0
        pet_happiness = 0

        if victory:
            coins = 20 + (performance_score // 10)
            pet_happiness = 15 + ((player_health_remaining - 1000) // 5)
            print(green(f"🎉 VICTORY! {self.player_pet.name} won the battle!"))
        else:
            coins = 5 + (performance_score // 20)
            pet_happiness = 5 + ((player_health_remaining - 1000) // 10)
            print(red(f"💔 Defeat... {self.player_pet.name} was defeated."))
        print("\n" + LINE)
        print("BATTLE RESULTS")
        print(LINE)
        print(f"Performance Score: {performance_score}/100")
        print(f"Health Remaining: {player_health_remaining}")
        print(f"Coins Earned: {'{:,}'.format(coins * 1000)}")
        print(f"Pet Happiness: (+{pet_happiness})")
        print(LINE)

        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        """Run the battle contest flow and return rewards (if setup succeeds)."""
        res = self.setup(player, pet)
        if res:
            self.build_question()
            battle_result = self.build_game()
            evaluation = self.evaluate(battle_result)
            return self.reward(evaluation)

"""Battle Contest minigame implementation (conforms to MinigameStrategy interfaces)."""

import time
from random import randint, choice
from typing import Any, List
from .base_class import MinigameStrategy
from utils.ports import ConsoleIO, InputPort, OutputPort
from utils.colorize import red, green
from constants.configs import UIConfig as UIC


class BattleContest(MinigameStrategy):
    """Simple multi-round pet-battle simulation against another player's pet."""

    name = "Battle Tournament"

    def __init__(self, io: InputPort | OutputPort | None = None):
        self.io: InputPort | OutputPort = io or ConsoleIO()
        self._opponents: List[Any] = []

    def set_opponents(self, opponents: List[Any]) -> None:
        """Dependency Injection: Provide the list of potential opponents."""
        self._opponents = opponents

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

        # FIX: Use injected self._opponents instead of User.users.values()
        candidates = self._opponents if self._opponents else []
        other_players_with_pets = list(filter(lambda user: user != self.player and user.pets, candidates))
        
        if other_players_with_pets:
            self.opponent = choice(other_players_with_pets)
            self.opponent_pet = choice(self.opponent.pets)
        else:
            self.io.write(red("\nOther players currently doesn't have any pets yet!\n"))
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
        self.io.write("\n" + UIC.LINE)
        self.io.write(f"PET BATTLE TOURNAMENT -> ROUND - {self.current_round}".center(len(UIC.LINE)))
        self.io.write(UIC.LINE)
        self.io.write("\n" + UIC.LINE)
        self.io.write(f"Your Pet: {self.player_pet.name} {self.player_pet.emoji}")
        self.io.write(f"Health: {self.player_health}")
        self.io.write(f"Strength: {self.player_pet_stats['strength']}")
        self.io.write(f"Agility: {self.player_pet_stats['agility']}")
        self.io.write('-' * len(UIC.LINE))

        if self.opponent_pet:
            self.io.write(f"Opponent: {self.opponent_pet.name} {self.opponent_pet.emoji}")
            self.io.write(f"Health: {self.opponent_health}")
            self.io.write(f"Strength: {self.player_pet_stats['strength']}")
            self.io.write(f"Agility: {self.player_pet_stats['agility']}")

        self.io.write(UIC.LINE)
        self.io.write("\nBattle Options:")
        self.io.write(UIC.LINE)
        self.io.write("1. Attack 🗡️")
        self.io.write("2. Defend 🛡️")
        self.io.write("3. Special Move ✨")
        self.io.write("4. Heal ❤️‍🩹")
        self.io.write(UIC.LINE)

    def get_input(self):
        """Prompt and validate a numeric choice for the battle action."""
        while True:
            try:
                choice_val = int(self.io.read("Choose your action (1-4): "))
                if 1 <= choice_val <= 4:
                    return choice_val
                self.io.write(red("Please enter a number between 1-4!"))
            except ValueError:
                self.io.write(red("Please enter a valid number!"))

    def build_question(self) -> Any:
        """Prepare the battle sequence and announce start."""
        self.io.write("\n" + UIC.LINE)
        self.io.write("Battle Starting!")
        self.io.write(UIC.LINE)
        self.io.write(f"{self.player_pet.name} {self.player_pet.emoji} VS {self.opponent_pet.name} {self.opponent_pet.emoji}")
        self.io.write("Prepare for battle!")
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

    def _execute_player_action(self, choice_val: int) -> None:
        """Execute the player's chosen action."""
        if choice_val == 1:
            self._player_attack()
        elif choice_val == 2:
            self._player_defend()
        elif choice_val == 3:
            self._player_special_move()
        elif choice_val == 4:
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
        self.io.write(f"\n{self.player_pet.name} attacks for {damage} damage ⚔️!")

    def _player_defend(self) -> None:
        """Player defends, temporarily reducing incoming damage (display only)."""
        defense_bonus = randint(2, 5) * 3000
        self.io.write(f"\n{self.player_pet.name} defends 🛡️!")
        self.io.write(f"Damage reduction: {defense_bonus}")

    def _player_special_move(self) -> None:
        """Player uses special move (only on even rounds)."""
        if self.current_round % 2 == 0:
            special_damage = (randint(10, 15) + self.player_pet_stats["strength"] // 2) * 600
            self.opponent_health -= special_damage
            self.io.write(f"\n{self.player_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            self.io.write(red("\nSpecial moves are locked in odd rounds!"))

    def _player_heal(self) -> None:
        """Player heals if heal limit not exceeded."""
        if self.player_heal_count < self.player_heal_limit:
            heal_amount = randint(8, 12) * 500
            self.player_health += heal_amount
            self.io.write(f"\n{self.player_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.player_heal_count += 1
        else:
            self.io.write(red("\nYou already healed 3 times!"))

    def _opponent_attack(self) -> None:
        """Opponent attacks the player."""
        damage = (randint(4, 8) + self.opponent_pet_stats["strength"] // 3) * 300
        self.player_health -= damage
        self.io.write(f"{self.opponent_pet.name} attacks for {damage} damage ⚔️!")

    def _opponent_defend(self) -> None:
        """Opponent defends (display only)."""
        defense_bonus = randint(1, 4) * 3000
        self.io.write(f"{self.opponent_pet.name} defends 🛡️!")
        self.io.write(f"Damage reduction: {defense_bonus}")

    def _opponent_special_move(self) -> None:
        """Opponent special move (only on odd rounds)."""
        if self.current_round % 2 != 0:
            special_damage = (randint(8, 12) + self.opponent_pet_stats["strength"] // 2) * 600
            self.player_health -= special_damage
            self.io.write(f"{self.opponent_pet.name} uses special move for {special_damage} damage ✨!")
        else:
            self.io.write(red("\nOpponent's special moves are restricted on even rounds!"))

    def _opponent_heal(self) -> None:
        """Opponent heals if heal limit not exceeded."""
        if self.opponent_heal_count < self.opponent_heal_limit:
            heal_amount = randint(6, 10) * 500
            self.opponent_health += heal_amount
            self.io.write(f"{self.opponent_pet.name} heals for {heal_amount} health ❤️‍🩹!")
            self.opponent_heal_count += 1
        else:
            self.io.write(red("\nOpponent's healing ability are restricted to 5 times only!"))

    def _determine_battle_outcome(self) -> None:
        """Determine and display the battle outcome and update counters."""
        if self.opponent_health <= 0:
            self.io.write(f"{self.opponent_pet.name} was defeated 🎉!")
            self.player_won += 1
            self.current_round += 1

        if self.player_health <= 0:
            self.io.write(f"{self.player_pet.name} was defeated 🎉!")
            self.opponent_won += 1

        if self.player_health <= 0 and self.opponent_health <= 0:
            self.io.write("It's a draw! 🤺")

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
            self.io.write(green(f"🎉 VICTORY! {self.player_pet.name} won the battle!"))
        else:
            coins = 5 + (performance_score // 20)
            pet_happiness = 5 + ((player_health_remaining - 1000) // 10)
            self.io.write(red(f"💔 Defeat... {self.player_pet.name} was defeated."))
        self.io.write("\n" + UIC.LINE)
        self.io.write("BATTLE RESULTS")
        self.io.write(UIC.LINE)
        self.io.write(f"Performance Score: {performance_score}/100")
        self.io.write(f"Health Remaining: {player_health_remaining}")
        self.io.write(f"Coins Earned: {'{:,}'.format(coins * 1000)}")
        self.io.write(f"Pet Happiness: (+{pet_happiness})")
        self.io.write(UIC.LINE)

        return {"currency": coins, "pet_happiness": pet_happiness}

    def play(self, player, pet):
        """Run the battle contest flow and return rewards (if setup succeeds)."""
        res = self.setup(player, pet)
        if res:
            self.build_question()
            battle_result = self.build_game()
            evaluation = self.evaluate(battle_result)
            return self.reward(evaluation)
        return {"currency": 0, "pet_happiness": 0}
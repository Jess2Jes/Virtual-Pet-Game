from .baseClass import MinigameStrategy
from random import choice, shuffle
from features.user import User
from constants.configs import LINE
from utils.colorize import red, green, blue
import time
from colorama import init

init(autoreset=True)

class Uno(MinigameStrategy):
    """A simple UNO card minigame to play with your little pet."""

    name = "UNO Card"

    COLORS = ['RED', 'YELLOW', 'GREEN', 'BLUE']
    VALUES = [str(num) for num in range(0, 10)]
    ACTION_CARDS = ['Skip', 'Reverse', 'DrawTwo']
    WILD_CARDS = ['Wild ColourChanger', 'Wild DrawFour']

    def setup(self, player, pet):
        self.player = player
        self.pet = pet
        self.deck = []
        self.top_card = None
        self.player_hand = []
        self.pet_hand = []
        self.discard = []
        self.turns = 0
        self.winner = None
        self.current_player_index = 0
        self.skip = False
        self.players = [
            {'name': 'You', 'hand': [], 'emoji': '👤'},
            {'name': self.pet.name, 'hand': [], 'emoji': self.pet.emoji},
        ]
        other_players_with_pets = list(filter(lambda user: user != self.player and user.pets, User.users.values()))
        if other_players_with_pets:
            self.opponent = choice(other_players_with_pets)
        else:
            self.opponent = None
        self.direction = 1

    def build_deck(self):
        """Builds and returns a full UNO deck."""

        self.deck = []

        # Number Cards
        for color in Uno.COLORS:
            self.deck.append(f"{color} 0")
            for v in Uno.VALUES[1:]:
                self.deck.append(f"{color} {v}")
                self.deck.append(f"{color} {v}")
        
        # Action Cards (2 of each)
        for color in Uno.COLORS:
            for action in Uno.ACTION_CARDS:
                self.deck.append(f"{color} {action}")
                self.deck.append(f"{color} {action}")
        
        # Wild Cards (4 of each)
        for wild in Uno.WILD_CARDS:
            for _ in range(4):
                self.deck.append(wild)
        
        shuffle(self.deck)
        return self.deck

    @staticmethod
    def display_menu():
        """Show a description and choices to the player."""
        print("\n" + LINE)
        print("🃏 UNO Card Minigame 🃏")
        print(LINE)
        print("Play this classic UNO card minigame with your pet!")
        print("\nRules:")
        print(LINE)
        print("- Each player will be given cards depending on game choices.")
        print("- Play one card matching the discard in color, number or symbol.")
        print("- Skip: Next player misses turn")
        print("- Reverse: Changes direction (3+ players)")
        print("- DrawTwo: Next player draws 2 cards")
        print("- Wild: Choose any color")
        print("- Wild DrawFour: Choose color and next player draws 4")
        print(LINE)
    
    @staticmethod
    def can_play(card, top_card):
        """Return True if card can be played on top_card."""
        card_parts = card.split()
        top_parts = top_card.split()

        card_color = card_parts[0]
        card_value = ' '.join(card_parts[1:])

        top_color = top_parts[0]
        top_value = ' '.join(top_parts[1:]) if len(top_parts) > 1 else None

        if "Wild" in card_color:
            return True
        
        if top_parts[0] == "Wild" and len(top_parts) > 1:
            chosen_color = top_parts[1]  
            return card_parts[0] == chosen_color
        
        if top_color in Uno.COLORS and top_value is None:
            return card_color == top_color
        
        return card_color == top_color or card_value == top_value
    
    def draw_card(self):
        """Draw a card; reshuffle discard pile if deck is empty."""
        if not self.deck:
            top = self.discard.pop()
            self.deck.extend(self.discard)
            self.discard.clear()
            self.discard.append(top)
            shuffle(self.deck)

        return self.deck.pop()

    def get_valid_moves(self, hand):
        """Get all valid moves from a hand."""
        return [card for card in hand if self.can_play(card, self.top_card)]

    def get_input(self, player):
        """Get and validate user input for their turn."""
        print(f"\n{player['name']}'s Turn:")
        print(LINE)
        print("Top Card:", self.top_card)

        print("\nYour Hand:")
        for i, c in enumerate(player['hand']):
            print(f" {i + 1}. {c}")
        print(LINE)

        valid_moves = self.get_valid_moves(player['hand'])

        if valid_moves:
            print("\nValid moves:")
            for i, c in enumerate(valid_moves):
                print(f"{i + 1}. {c}")
            print(LINE)
            choice = input("Play (h) or draw (p)? ").strip().lower()
            return choice, valid_moves
        else:
            print(red("\nThere is no more valid moves for player!"))
            return 'p', None

    
    def build_question(self):
        """Build the game setup - optional difficulty or rules."""

        total_players = self._multiplayer_choice()
        if total_players > 2:
            self._setup_player(total_players)

        print("\nUNO Games:")
        print(LINE)
        print("1. Standard UNO (7 cards each)")
        print("2. Quick UNO (5 cards each)")
        print("3. Challenge UNO (10 cards each)")
        print(LINE)

        try:
            choice = int(input("Choose your game modes (1/2/3/4): ").strip())
        except ValueError:
            choice = 1
        if choice not in range(1, 5):
            choice = 1

        self.build_deck()

        self.top_card = self.draw_card()
        while "Wild" in self.top_card:
            self.deck.append(self.top_card)
            shuffle(self.deck)
            self.top_card = self.draw_card()
        
        self.discard.append(self.top_card)

        if choice == 1:
            hand_size = 7
        elif choice == 2:
            hand_size = 5
        else:
            hand_size = 10

        for player in self.players:
            player['hand'] = [self.draw_card() for _ in range(hand_size) if self.deck]
    
    def _multiplayer_choice(self):
        """Choose number of players."""

        print("\nUNO Multiplayer Games:")
        print(LINE)
        print("1. 2 Players")
        print("2. 3 Players")
        print("3. 4 Players")
        print("4. 5 Players")
        print(LINE)
        try:
            player_count = int(input("Choose your game modes (1/2/3/4): ").strip())
        except ValueError:
            player_count = 1

        if player_count not in range(1, 5):
            player_count = 1

        total_players = player_count + 1

        return total_players
    
    def _setup_player(self, total_players=3):
        """Setup players list based on total players."""

        if not self.opponent:
            print(red("\nNo other players available!"))

        elif len(self.opponent.pets) < total_players - 2:
            print(red("\nNot enough player!"))
        else:
            list_player_names = [player['name'] for player in self.players]
            for _ in range(total_players - 2):
                opponent_pet = choice([pet for pet in self.opponent.pets 
                    if pet.name not in list_player_names])
                self.players.append({
                    'name': opponent_pet.name,
                    'hand': [],
                    'emoji': opponent_pet.emoji
                })
                list_player_names.append(opponent_pet.name)

    def _play_card(self, player, card):
        """Play a card from hand. Returns played_card."""

        next_player_idx = (self.current_player_index + self.direction) % len(self.players)

        if card in player['hand']:
            player['hand'].remove(card)
            print(f"\n{player['emoji']} {player['name']}: {card}")
        
        if 'Wild' in card:
            if player['name'].lower() != 'you':
                color = choice(Uno.COLORS)
                print(f"{player['emoji']} {player['name'].title()} changes color to:", color)
            else:
                color = None
                while color not in Uno.COLORS:
                    color = input("Choose color (RED/YELLOW/GREEN/BLUE): ").strip().upper()
            
            if 'DrawFour' in card:
                for _ in range(4):
                    card = self.draw_card()
                    self.players[next_player_idx]['hand'].append(card)
                self.skip = True
            
            played_card = f"Wild {color}"

            self.discard.append(played_card)
            return played_card

        if 'DrawTwo' in card:
            for _ in range(2):
                card = self.draw_card()
                self.players[next_player_idx]['hand'].append(card)
            self.skip = True
        
        if 'Skip' in card:
            self.skip = True

        if 'Reverse' in card and len(self.players) > 2:
            self.direction *= -1
            print(f"Direction reversed! Now going {'↻ clockwise' if self.direction == 1 else '↺ counter-clockwise'}")
        
        self.discard.append(card)
        return card
    
    def _handle_draw(self, player):
        """Handle drawing a card when no valid moves."""

        print(blue("\nDrawing..."))
        new_card = self.draw_card()
        player['hand'].append(new_card)

        print(f"{player['emoji']} {player['name'].title()} drew:", new_card)
    
        if self.can_play(new_card, self.top_card):
            print(green(f"{player['name']} can play it!"))
            return self._play_card(player, new_card)
        else:
            print(red("Cannot play. Turn ends."))
            return self.top_card
        
    def next_player(self):
        """Move to next player based on direction."""

        if self.skip:
            self.skip = False
            self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
            if self.players[self.current_player_index]['name'].lower() == 'you':
                print(blue("Your turn skipped!"))
            else:
                print(blue(f"{self.players[self.current_player_index]['name']}'s turn skipped!"))
            self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
        else:
            self.current_player_index = (self.current_player_index + self.direction) % len(self.players)

    def player_turn(self, player):
        """Handle the player's full turn."""

        valid = False

        while not valid:
            choice, valid_moves = self.get_input(player['name'], player['hand'])

            if choice == 'h':
                try: 
                    idx = int(input('\nEnter card index: ')) - 1
                    card = valid_moves[idx]
                    valid = True
                except (ValueError, IndexError):
                    print(red("Invalid input! Please try again."))
            else:
                return self._handle_draw(player)
        
        return self._play_card(player, card)
    
    def opponent_turn(self, player):
        """Handle pet(s) move."""

        print(f"\n{player['name']}'s Turn...")
        print(LINE)
        time.sleep(1)
        valid_moves = self.get_valid_moves(player['hand'])

        if valid_moves:
            card = choice(valid_moves)

            return self._play_card(player, card)
        
        else:
            return self._handle_draw(player)

    def build_game(self):
        """Run the interactive game loop."""

        print("\nList of UNO Participants: ")
        print(LINE)
        for i, p in enumerate(self.players):
            print(f" {i + 1}. {p['name']}")

        print(f"\nDealing with {len(self.players[0]['hand'])} cards each...")
        time.sleep(1)

        while True:
            current_player = self.players[self.current_player_index]
            print(f"Top Card: {self.top_card}")
            if current_player['name'].lower() == "you":
                card = self.player_turn(current_player)
            else:
                card = self.opponent_turn(current_player)

            if not current_player['hand']:
                self.winner = current_player['name']
                break

            if card and card != self.top_card:
                self.top_card = card
            
            if len(current_player['hand']) == 1 and current_player['name'].lower() != 'you':
                print(green(f"\n{current_player['emoji']} {current_player['name']}: UNO!"))
            
            self.next_player()
            self.turns += 1

        return {
            "winner": self.winner,
            "turns": self.turns,
            "player_cards_left": len(self.player_hand),
            "pet_cards_left": len(self.pet_hand),
            "deck_size": len(self.deck)
        }
    
    def evaluate(self, answer):
        """Evaluate the game results."""

        winner = answer.get('winner')
        turns = answer.get('turns', 0)
        player_cards = answer.get('player_cards_left', 0)
        
        if winner == "You":
            outcome = "Win"
        else:
            outcome = "Lose"

        return {
            "outcome": outcome,
            "turns": turns,
            "player_cards_left": player_cards,
            "winner": winner
        }
    
    def reward(self, result):
        """Convert evaluation results into currency/pet happiness rewards."""
        outcome = result.get('outcome')
        turns = result.get('turns', 0)
        player_cards = result.get('player_cards_left', 0)
        winner = result.get('winner')
        
        if outcome == "Win":
            coins = 30 + max(0, 20 - turns) + max(0, 10 - player_cards)
            pet_happiness = 2
            print(green(f"\n🎉 You won in {turns} turns!"))
        else:
            if winner == self.pet.name:
                coins = max(5, 15 - player_cards)
                pet_happiness = 10
                print(green(f"\n🎉 Your pet won in {turns} turns!"))
            else:
                coins = max(5, 35 - player_cards)
                pet_happiness = 5
                print(f"\nThe winner is: {winner}!")
                print(red("\n💪 Better luck next time!"))
        
        print(f"Reward: Rp. {'{:,}'.format(coins * 1000)}. Pet happiness (+{pet_happiness})")
        print(green(f"You received Rp. {'{:,}'.format(coins * 1000)} 🎉"))

        return {"currency": coins, "pet_happiness": pet_happiness}
    
    def play(self, player, pet):
        """Run the full UNO game and return rewards."""
        self.setup(player, pet)
        self.display_menu()
        self.build_question()
        summary = self.build_game()
        result = self.evaluate(summary)
        reward = self.reward(result)
        return reward

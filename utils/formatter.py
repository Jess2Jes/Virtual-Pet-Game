# Formatter : for pet stats table, pet after-care stats, account info and timezone
from typing import Dict
from os import system, name

def clear():
    """Clear the console screen based on the operating system."""
    system("cls" if name == "nt" else "clear")
    
    
"""
formatter.py

Provides a small ASCII-box formatter used by the Virtual Pet Game.

This module contains:
- Formatter: helper class to render consistent boxed text displays for:
    - user status (username, number of pets)
    - time status (current time, days passed)
    - individual pet upgrade/status displays (various stat combinations)
    - full pet status box with many stats

Notes:
- The original implementation included Indonesian comments; those have been translated
  to English and additional docstrings were added for clarity. No runtime logic was changed.
"""

class Formatter:
    """
    Formatter for rendering ASCII-styled boxed information.

    Typical usage:
        f = Formatter()
        box = f.format_status_box(stats_dict)
        print(box)

    Attributes:
        max_length: running maximum width used when building boxes (initially 0).
        max_len: hard character limit for truncated lines (default: 55).
    """

    def __init__(self):
        self.max_length = 0
        self.max_len = 55

    def truncate(self, text: str, max_len: int, ellipsis: str = "...", strip: bool = False) -> str:
        """
        Truncate a string to a maximum length, appending an ellipsis if truncated.
        
        Parameters:
        - text: string to truncate
        - max_len: maximum total length including ellipsis
        - ellipsis: string to append if truncated
        - strip: whether to strip trailing whitespace before adding ellipsis
        """
        if len(text) <= max_len:
            return text
        truncated = text[:max_len - len(ellipsis)]
        if strip:
            truncated = truncated.rstrip()
        return truncated + ellipsis

    def format_username_box(self, username: str, pets: int) -> str:
        """
        Create a boxed "USER STATUS" block displaying the logged-in username and number of pets.

        Args:
            username: the username to display.
            pets: a collection (or length) representing the user's pets; code uses len(pets).

        Returns:
            A multi-line string containing an ASCII box.
        """
        max_length = self.max_length

        lines = [
            self.truncate("USER STATUS", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Logged in as : {username}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Number of pets: {len(pets)}", self.max_len, ellipsis="", strip=False),
        ]

        for line in lines:
            max_length = max(max_length, len(line) + 5)

        box = "\n"
        box += f"┌{'─' * max_length}┐\n"
        box += f"│{lines[0].center(max_length)}│\n"
        box += f"├{'─' * max_length}┤\n"

        for line in lines[1:]:
            if line != lines[-1]:
                box += f"│{line.ljust(max_length)}│\n"
                box += f"├{'─' * max_length}┤\n"
            else:
                box += f"│{line.ljust(max_length)}│\n"

        box += f"└{'─' * max_length}┘\n"

        return box

    def format_time_box(self, hours: str, days: str) -> str:
        """
        Create a boxed "TIME STATUS" block showing the current time and days passed.

        Args:
            hours: human-readable current time.
            days: number of days passed as string.

        Returns:
            Multi-line ASCII box string.
        """
        max_length = self.max_length

        lines = [
            self.truncate("TIME STATUS", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Current Time : {hours}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Days Passed  : {days}", self.max_len, ellipsis="", strip=False),
        ]

        for line in lines:
            max_length = max(max_length, len(line) + 5)

        box = "\n"
        box += f"┌{'─' * max_length}┐\n"
        box += f"│{lines[0].center(max_length)}│\n"
        box += f"├{'─' * max_length}┤\n"

        for line in lines[1:]:
            if line != lines[-1]:
                box += f"│{line.ljust(max_length)}│\n"
                box += f"├{'─' * max_length}┤\n"
            else:
                box += f"│{line.ljust(max_length)}│\n"

        box += f"└{'─' * max_length}┘\n"

        return box

    def format_upgrade_stats(self, pet, stats: Dict) -> str:
        """
        Format a small status box for a pet after an upgrade or care action.

        The function chooses which stats to display depending on how many keys are present
        in the provided stats dictionary (3 or 4 or other combinations).

        Args:
            pet: an object representing the pet, expected to have attributes used below
                 (e.g., pet.fat, pet.health, pet.energy, pet.age, pet.hunger, pet.happiness, pet.sanity).
            stats: a dict describing which stats are relevant for this display (keys control layout).

        Returns:
            Multi-line ASCII box string showing the chosen stats.
        """
        max_length = self.max_length

        title = self.truncate(f"{pet.name}'s Status", self.max_len, ellipsis="", strip=False)

        if len(stats.keys()) == 4:
            lines = [
                self.truncate(f"Fat        : {pet.fat}", self.max_len, ellipsis="", strip=False),
                self.truncate(f"Health     : {pet.health}", self.max_len, ellipsis="", strip=False),
                self.truncate(f"Energy     : {pet.energy}", self.max_len, ellipsis="", strip=False),
                self.truncate(f"Age        : {pet.age}", self.max_len, ellipsis="", strip=False),
            ]

        elif len(stats.keys()) == 3:

            if ("fat", "hunger", "happiness") == tuple(stats.keys()):
                lines = [
                    self.truncate(f"Hunger     : {pet.hunger}", self.max_len, ellipsis="", strip=False),
                    self.truncate(f"Happiness  : {pet.happiness}", self.max_len, ellipsis="", strip=False),
                    self.truncate(f"Fat        : {pet.fat}", self.max_len, ellipsis="", strip=False),
                ]

            else:
                lines = [
                    self.truncate(f"Hunger     : {pet.hunger}", self.max_len, ellipsis="", strip=False),
                    self.truncate(f"Happiness  : {pet.happiness}", self.max_len, ellipsis="", strip=False),
                    self.truncate(f"Energy     : {pet.energy}", self.max_len, ellipsis="", strip=False),
                ]

        else:
            if ("sanity", "happiness") == tuple(stats.keys()):
                lines = [
                    self.truncate(f"Sanity     : {pet.sanity}", self.max_len, ellipsis="", strip=False),
                    self.truncate(f"Happiness  : {pet.happiness}", self.max_len, ellipsis="", strip=False),
                ]
            else:
                lines = [self.truncate(f"Energy: {pet.energy}", self.max_len, ellipsis="", strip=False), self.truncate(f"Hunger: {pet.hunger}", self.max_len, ellipsis="", strip=False)]
        for line in lines:
            max_length = max(max_length, len(title), len(line) + 5)

        box = "\n"
        box += f"┌{'─' * max_length}┐\n"
        box += f"│{title.center(max_length)}│\n"
        box += f"├{'─' * max_length}┤\n"

        for line in lines:
            box += f"│{line.ljust(max_length)}│\n"

        box += f"└{'─' * max_length}┘\n"

        return box

    def format_status_box(self, stats: Dict[str, str]) -> str:
        """
        Create a full pet status box showing multiple attributes.

        The function builds a list of lines from the stats dict, then computes the
        maximum line length to align all rows inside a consistent ASCII box.

        Args:
            stats: dictionary containing pet attributes. Expected keys include:
                'name', 'type', 'age', 'hunger', 'fat', 'sanity', 'happiness',
                'energy', 'health', 'mood', 'summary', 'age_summary'.

        Returns:
            Multi-line ASCII box string representing the pet's current status.
        """
        max_length = self.max_length

        lines = [
            self.truncate(f"{stats['name']}, the {stats['type']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Age        : {stats['age']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Hunger     : {stats['hunger']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Fat        : {stats['fat']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Sanity     : {stats['sanity']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Happy      : {stats['happiness']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Energy     : {stats['energy']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Health     : {stats['health']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Mood       : {stats['mood']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Status     : {stats['summary']}", self.max_len, ellipsis="", strip=False),
            self.truncate(f"Age Status : {stats['age_summary']}", self.max_len, ellipsis="", strip=False),
        ]
        # Find the longest text length in the lines list and use it for box width.
        # Example lengths:
        #   "Mochi the Cat"           -> 13
        #   "Age        : 2"          -> 14
        #   "Hunger     : 90"         -> 15
        #   "Happy      : 100"        -> 16
        #   "Mood       : Happy"      -> 18
        #   "Status     : Critical"   -> 21
        # The max_length becomes 21 in that example and all box lines are aligned to width 21.

        for line in lines:
            max_length = max(max_length, len(line))

        box = "\n"
        box += f"┌{'─' * max_length}┐\n"
        box += f"│{lines[0].center(max_length)}│\n"
        box += f"├{'─' * max_length}┤\n"

        for line in lines[1:]:
            box += f"│{line.ljust(max_length)}│\n"

        box += f"└{'─' * max_length}┘\n"

        return box
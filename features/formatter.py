# Formatter : untuk tabel pet stats, pet after care stats, account info dan timezone
from typing import Dict

GARIS = "─"*101
class Formatter:
    def __init__(self):
        self.max_length = 0
        self.max_len = 55

    def truncate(self, text: str) -> str:  # maksimal panjang teks
        ''' Membuat fungsi truncate untuk memotong teks agar tidak terlalu panjang
            sehingga tidak merusak tampilan baris dalam box'''
        if len(text) <= self.max_len:
            return text
        else:
            return text[:self.max_len - 3] + "..."
    
    def format_username_box(self, username: str, pets: int) -> str:

        max_length = self.max_length
        
        lines = [
            self.truncate("USER STATUS"),
            self.truncate(f"Logged in as : {username}"),
            self.truncate(f"Number of pets: {len(pets)}")
        ]

        for line in lines:
            max_length = max(max_length, len(line) + 5)

        box = "\n"
        box += f"┌{'─' * max_length}┐\n"
        box += f"│{lines[0].center(max_length)}│\n"
        box += f"├{'─' * max_length}┤\n"

        for line in lines[1:]:
            if (line != lines[-1]):
                box += f"│{line.ljust(max_length)}│\n"
                box += f"├{'─' * max_length}┤\n"
            else:
                box += f"│{line.ljust(max_length)}│\n"
        
        box += f"└{'─' * max_length}┘\n"
            
        return box
        
    def format_time_box(self, hours: str, days: str) -> str:

        max_length = self.max_length

        lines = [
            self.truncate("TIME STATUS"),
            self.truncate(f"Current Time : {hours}"),
            self.truncate(f"Days Passed  : {days}")
        ]

        for line in lines:
            max_length = max(max_length, len(line) + 5)

        box = "\n"
        box += f"┌{'─' * max_length}┐\n"
        box += f"│{lines[0].center(max_length)}│\n"
        box += f"├{'─' * max_length}┤\n"

        for line in lines[1:]:
            if (line != lines[-1]):
                box += f"│{line.ljust(max_length)}│\n"
                box += f"├{'─' * max_length}┤\n"
            else:
                box += f"│{line.ljust(max_length)}│\n"
        
        box += f"└{'─' * max_length}┘\n"
            
        return box

    def format_upgrade_stats(self, pet, stats: Dict) -> str:

        max_length = self.max_length

        title = self.truncate(f"{pet.name}'s Status")

        if (len(stats.keys()) == 4):
            lines = [
                self.truncate(f"Fat        : {pet.fat}"),
                self.truncate(f"Health     : {pet.health}"),
                self.truncate(f"Energy     : {pet.energy}"),
                self.truncate(f"Age        : {pet.age}")
            ]

        elif (len(stats.keys()) == 3):

            if (("fat", "hunger", "happiness") == tuple(stats.keys())):
                lines = [
                    self.truncate(f"Hunger     : {pet.hunger}"),
                    self.truncate(f"Happiness  : {pet.happiness}"),
                    self.truncate(f"Fat        : {pet.fat}")
                ] 
                
            else:
                lines = [
                    self.truncate(f"Hunger     : {pet.hunger}"),
                    self.truncate(f"Happiness  : {pet.happiness}"),
                    self.truncate(f"Energy     : {pet.energy}")
                ]

        else:
            if (("sanity", "happiness") == tuple(stats.keys())):
                lines = [
                    self.truncate(f"Sanity     : {pet.sanity}"),
                    self.truncate(f"Happiness  : {pet.happiness}")
                ]
            else:
                lines = [
                    self.truncate(f"Energy: {pet.energy}"),
                    self.truncate(f"Hunger: {pet.hunger}")
                ]

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

        max_length = self.max_length

        lines = [
            self.truncate(f"{stats['name']}, the {stats['type']}"),
            self.truncate(f"Age        : {stats['age']}"),
            self.truncate(f"Hunger     : {stats['hunger']}"),
            self.truncate(f"Fat        : {stats['fat']}"),      
            self.truncate(f"Sanity     : {stats['sanity']}"),
            self.truncate(f"Happy      : {stats['happiness']}"),
            self.truncate(f"Energy     : {stats['energy']}"),
            self.truncate(f"Health     : {stats['health']}"),
            self.truncate(f"Mood       : {stats['mood']}"),
            self.truncate(f"Status     : {stats['summary']}"),
            self.truncate(f"Age Status : {stats['age_summary']}")
        ]
        ''' Cari panjang teks terpanjang di dalam list lines.
            max_length akan menyimpan nilai panjang terbesar.

            Contoh:
            lines = [
                "Mochi the Cat",          # length = 13
                "Age        : 2",         # length = 14
                "Hunger     : 90",        # length = 15
                "Fat        : 0",         # length = 14
                "Sanity     : 50",        # length = 15
                "Happy      : 100",       # length = 16
                "Energy     : 52",        # length = 15
                "Health     : 20",        # length = 15
                "Mood       : Happy",     # length = 18
                "Status     : Critical",  # length = 21
                "Age Status : Teen",      # length = 17
            ]

            Hasil:
            max_length = 21
            (semua baris box akan disesuaikan dengan lebar 21) 
        '''

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


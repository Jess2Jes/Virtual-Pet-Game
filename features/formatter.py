# Formatter : untuk tabel pet stats
class Formatter:

    def __init__(self):
        self.max_length = 0
        self.max_len = 55

    def truncate(self, text):  # maksimal panjang teks
        ''' Membuat fungsi truncate untuk memotong teks agar tidak terlalu panjang
            sehingga tidak merusak tampilan baris dalam box'''
        if len(text) <= self.max_len:
            return text
        else:
            return text[:self.max_len - 3] + "..."

    def format_status_box(self, stats):

        lines = [
            self.truncate(f"{stats['name']}, the {stats['type']}"),
            self.truncate(f"Age        : {stats['age']}"),
            self.truncate(f"Hunger     : {stats['hunger']}"),
            self.truncate(f"Fat        : {stats['fat']}"),      # NEW LINE
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
                "Mochi the Cat",     # length = 13
                "Age     : 2",       # length = 10
                "Hunger  : 90",      # length = 12
                "Happy   : 50",      # length = 12
                "Energy  : 10",      # length = 12
                "Health  : 100",     # length = 13
                "Mood    : Hungry"   # length = 17  <-- ini paling panjang
            ]

            Hasil:
            max_length = 17
            (semua baris box akan disesuaikan dengan lebar 17) 
        '''

        for line in lines:
            self.max_length = max(self.max_length, len(line))

        box = "\n"
        box += f"┌{'─' * self.max_length}┐\n"
        box += f"│{lines[0].center(self.max_length)}│\n"
        box += f"├{'─' * self.max_length}┤\n"

        for line in lines[1:]:
            box += f"│{line.ljust(self.max_length)}│\n"

        box += f"└{'─' * self.max_length}┘\n"
        return box

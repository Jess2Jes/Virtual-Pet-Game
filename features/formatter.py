def truncate(text, max_len=55):  # maksimal panjang teks
    ''' Membuat fungsi truncate untuk memotong teks agar tidak terlalu panjang
        sehingga tidak merusak tampilan baris dalam box'''
    if len(text) <= max_len:
        return text
    else:
        return text[:max_len - 3] + "..."

def format_status_box(stats):
    lines = [
        truncate(f"{stats['name']}, the {stats['type']}"),
        truncate(f"Age        : {stats['age']}"),
        truncate(f"Hunger     : {stats['hunger']}"),
        truncate(f"Fat        : {stats['fat']}"),      # NEW LINE
        truncate(f"Sanity     : {stats['sanity']}"),
        truncate(f"Happy      : {stats['happiness']}"),
        truncate(f"Energy     : {stats['energy']}"),
        truncate(f"Health     : {stats['health']}"),
        truncate(f"Mood       : {stats['mood']}"),
        truncate(f"Status     : {stats['summary']}"),
        truncate(f"Age Status : {stats['age_summary']}")
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

    
    max_length = 0
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
    
    
    
    

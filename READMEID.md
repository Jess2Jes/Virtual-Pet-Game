[English](README.md) | Indonesian
# 🐾 Virtual Pet Game

Game hewan peliharaan virtual berbasis konsol yang dibangun dengan konsep OOP.  

## 📖 Gambaran Umum
- Sistem pengguna dengan login dan registrasi  
- Banyak jenis hewan (Kucing, Kelinci, Dinosaurus, Naga, Pou)  
- Perawatan hewan: memberi makan, memandikan, menyembuhkan, tidur, jalan-jalan, bermain, berbicara  
- Toko dengan mata uang dalam game dan item  
- Tahapan hidup: bayi → remaja → dewasa → tua  
- Statistik yang memengaruhi kelangsungan hidup: kebahagiaan, lapar, kewarasan, kesehatan, lemak, energi  

## ✨ Fitur
- **Pengguna**: autentikasi dan mata uang  
- **Hewan**: statistik acak, pertumbuhan usia, ASCII art sesuai tahap  
- **Interaksi**: memberi makan, memandikan, jalan-jalan, ramuan, dan lainnya  
- **Toko**: makanan, sabun, ramuan dengan efek tertentu  
- **UI Status**: tampilan status di CLI yang terformat  
- **Waktu**: jam dalam game dan penghitung hari  

## 📂 Struktur Proyek
- `main.py` – titik masuk, menu, status sesi  
- `game.py` – loop permainan, interaksi hewan  
- `pet.py` – kelas VirtualPet, statistik, pertumbuhan, stok bersama  
- `animal.py` – subclass tiap spesies dengan ASCII art  
- `formatter.py` – pemotongan teks dan pemformat status box  
- `shop.py` – katalog item, logika pembelian  
- `user.py` – registrasi pengguna, autentikasi, mata uang  

Dokumentasi detail: [docs/structure.md](docs/structure.md)

## 🎮 Cara Menjalankan Game

1. Instal **Python 3.x**.  
2. Clone atau fork repository:  
   ```bash
   git clone https://github.com/Jess2Jes/Virtual-Pet-Game.git
   cd Virtual-Pet-Game
3. Jalankan `python main.py`

## 🚀 Rencana Pengembangan

- Simpan/muat hewan dan pengguna (JSON, pickle, atau database).  
- GUI (Tkinter, PyQT, atau web dengan Flask/FastAPI).  
- Lebih banyak hewan dan animasi ASCII art.  
- Mini-games dan event.  
- Interaksi multipemain/sosial.  
- Unit testing dan refactor ke services/models.  

## 👥 Penulis & Kontributor

- [Jess2Jes](https://github.com/Jess2Jes) — Pimpinan Proyek & Pengembang Utama  
- [Hans](https://github.com/Dendroculus) — Kontributor  
- [StevNard](https://github.com/StevNard) — Kontributor  


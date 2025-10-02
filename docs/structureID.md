# 📝 Dokumentasi Proyek – Virtual Pet Game
Dokumen ini menjelaskan struktur internal dan logika dari Virtual Pet Game.

## 📂 Rincian File

- **main.py**  
  Titik masuk program. Menangani menu, status sesi, dan mengintegrasikan modul inti (`game.py`, `shop.py`, `user.py`).

- **game.py**  
  Loop inti permainan.  
  Tanggung jawab:
  - 🐾 Pemilihan hewan peliharaan  
  - 🎮 Menu interaksi utama (makan, bermain, mandi, jalan-jalan, tidur, berbicara, ramuan)  
  - 📊 Pembaruan status  
  - ⏰ Perkembangan waktu  

- **pet.py**  
  Kelas `VirtualPet`:  
  - ❤️ Menyimpan statistik (kebahagiaan, lapar, kewarasan, kesehatan, lemak, energi)  
  - ⏳ Pertumbuhan usia dan tahapan hidup  
  - 🛒 Daftar stok bersama untuk makanan, sabun, dan ramuan  
  - 🐱 Metode perilaku: `feed()`, `bathe()`, `sleep()`, `health_care()`, dll.  

- **animal.py**  
  Subclass untuk tiap jenis hewan: Kucing, Kelinci, Dinosaurus, Naga, Pou  
  - 🍗 Menentukan makanan favorit  
  - 🎨 ASCII art per tahap kehidupan  

- **formatter.py**  
  - ✂️ `truncate(text, max_len)` – pemotong panjang teks  
  - 📦 `format_status_box(stats)` – kotak status dinamis di CLI  

- **shop.py**  
  - 🛍️ Katalog item makanan, sabun, dan ramuan  
  - 💰 Metode `buy()` yang mengurangi uang pengguna dan memperbarui stok  

- **user.py**  
  - 🔑 Registrasi dan autentikasi pengguna  
  - ✅ Menegakkan kebijakan password  
  - 🐾 Melacak hewan peliharaan yang dimiliki dan mata uang pengguna  

## 💰 Toko & Ekonomi
- 🍖 **Makanan**: memengaruhi rasa lapar dan kebahagiaan  
- 🧼 **Sabun**: memengaruhi kewarasan dan kebahagiaan  
- 🧪 **Ramuan**: berbagai efek (energi, kesehatan, pengurang lemak, percepatan umur)  
- 📦 Setiap item memiliki jumlah stok yang dibagikan ke semua pengguna  

## 📝 Catatan
- ⚖️ Statistik dibatasi 0–100 menggunakan `limit_stat()`  
- ⏳ Pertumbuhan usia ditangani oleh `time_past()` yang mengurangi statistik dan memperbarui tahap kehidupan  
- 🎲 Keacakan diterapkan pada statistik awal dan event jalan-jalan  
- 🛠️ Dirancang agar mudah diperluas untuk GUI, penyimpanan data, dan hewan tambahan  

Untuk instruksi bermain, lihat [README](../README.md)  

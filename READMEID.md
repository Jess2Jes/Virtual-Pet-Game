<div align="center">

[English](README.md) | Indonesian | [中文](READMECN.md)

</div>

<div align="center">

# 🐾 Game Peliharaan Virtual

</div>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.x-blue.svg" />
  <img alt="Konsep" src="https://img.shields.io/badge/konsep-PBO_%26_Pewarisan-blueviolet.svg" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" />
  <img alt="Status" src="https://img.shields.io/badge/status-Selesai-brightgreen.svg" />
</p>

Game simulasi peliharaan virtual berbasis konsol yang dibangun dengan Pemrograman Berbasis Objek (PBO) di Python. Pilih peliharaan, beri nama, lalu rawat sampai tumbuh melalui beberapa tahap kehidupan. Kelola statistik, ajak bermain, dan jaga agar tetap sehat dan bahagia!

---

## 🎮 Demo Gameplay

Seluruh permainan berjalan di terminal, menampilkan kotak status yang detail dan seni ASCII untuk setiap tahap kehidupan peliharaan.

**Buat peliharaan unik Anda sendiri:**
```text
───────────────────────────────── Create Your Own Pet ─────────────────────────────────────────
Name your pet: Mochi
─────────────────────────────────────────────────────────────────────────────────────────────────
Here's five types of species you can choose:
1. Cat
2. Rabbit
3. Dinosaur
4. Dragon
5. Pou
─────────────────────────────────────────────────────────────────────────────────────────────────
Choose his/her species (input type of species here): cat

─────────────────────────────────────────────────────────────────────────────────────────────────
Mochi, a cat, has born!
─────────────────────────────────────────────────────────────────────────────────────────────────
```

**Saksikan ia tumbuh dan lihat seni uniknya di setiap tahap kehidupan:**
```text
==================================================================================================

/|、      ......
(˚ˎ 。7  . miw! .
 |、˜〵   ......
じしˍ,)ノ
~~~~~~~~~~~~~~~
```

**Pantau kebutuhannya dengan panel status yang terperinci:**

<img src="assets/pet_stats.png" alt="Panel Status Peliharaan" />

---

## ✨ Fitur Utama

- **Peliharaan Beragam & Berkembang**: Pilih dari 5 spesies (**Kucing, Kelinci, Dinosaurus, Naga, Pou**) dan saksikan mereka tumbuh melalui tahap (**Bayi, Remaja, Dewasa, Tua**) dengan ASCII art unik.
- **Simulasi Peliharaan Mendalam**: Kelola statistik seperti **Rasa Lapar, Kewarasan, Kebahagiaan, Kesehatan, Lemak, Energi**. Mengabaikan kebutuhan dapat membuat kondisi peliharaan kritis.
- **Aksi Perawatan Interaktif**:
  - **Beri Makan**, **Mandi**, **Bermain**, **Bicara**, **Jalan-Jalan**, **Tidur**
- **Ekonomi & Toko Dalam Game**: Dapatkan mata uang dan beli makanan, sabun, serta ramuan spesial.
- **Autentikasi Pengguna**: Daftar, masuk, dan ubah kata sandi dengan validasi.
- **Sistem Waktu**: Sistem jam/hari dalam game; statistik berubah seiring waktu.

---

## 🛠️ Pameran Teknis

- **Desain PBO (OOP)**: Dibangun dari modul inti (`game`, `pet`, `user`, `shop`).
- **Pewarisan & Polimorfisme**: Kelas spesies mewarisi model peliharaan dasar dan memiliki perilaku/art unik.
- **Struktur Modular**: Fitur dan utilitas dipisah ke file/folder agar mudah dipelihara.

---

## 🚀 Cara Memulai

### Prasyarat
- Python 3.x

### Instalasi & Menjalankan
1. Clone repo
```bash
git clone https://github.com/Jess2Jes/Virtual-Pet-Game.git
cd Virtual-Pet-Game
```

2. Jalankan game
```bash
python main.py
```

3. Ikuti instruksi di layar untuk registrasi dan mulai bermain.

---

## 📂 Struktur Proyek

(Sesuai struktur repo saat ini)

```bash
Virtual-Pet-Game/
├── assets/
│   └── pet_stats.png
├── constants/
│   ├── arts/
│   │   ├── cat.py
│   │   ├── dino.py
│   │   ├── dragon.py
│   │   ├── pou.py
│   │   ├── rabbits.py
│   │   └── animalsArt.py
│   └── configs.py
├── datas/
│   ├── conversations.json
│   ├── jokes.json
│   └── words.txt
├── docs/
├── features/
│   ├── minigame/
│   ├── animal.py
│   ├── game.py
│   ├── memento.py
│   ├── pet.py
│   ├── save_manager.py
│   ├── shop.py
│   └── user.py
├── program_testing/
├── saves/
│   └── player_saves.json
├── utils/
├── main.py
├── README.md
├── READMEID.md
├── READMECN.md
└── LICENSE
```

---

## 🗺️ Rencana Pengembangan

- **Persistensi**: Perbaiki sistem save/load (atau migrasi ke SQLite).
- **Implementasi GUI**: Buat versi GUI (Tkinter / PyQT).
- **Konten Tambahan**: Tambah spesies, item, dan event acak.
- **Mini-Games**: Perluas mini-game dan reward.
- **Testing**: Tambahkan unit test dan CI.

---

## 👥 Penulis & Kontributor

<table border="0" cellspacing="10" cellpadding="5">
  <tr>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/Jess2Jes">
        <img src="https://github.com/Jess2Jes.png" width="100" height="100" alt="Jess2Jes" style="border-radius: 50%;"/>
      </a>
      <br/>
      <a href="https://github.com/Jess2Jes">Jessica Gunawan</a>
    </td>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/Yoruxyv">
        <img src="https://github.com/Yoruxyv.png" width="100" height="100" alt="Hans" style="border-radius: 50%;"/>
      </a>
      <br/>
      <a href="https://github.com/Yoruxyv">Hans Valerie</a>
    </td>
    <td align="center" style="border: 1px solid #555; padding: 10px;">
      <a href="https://github.com/StevNard">
        <img src="https://github.com/StevNard.png" width="100" height="100" alt="StevNard"/>
      </a>
      <br/>
      <a href="https://github.com/StevNard">Steven Lienardi</a>
    </td>
  </tr>
</table>

---

## 📜 Lisensi

Proyek ini dilisensikan dengan lisensi MIT. Lihat [`LICENSE`](LICENSE) untuk detail.
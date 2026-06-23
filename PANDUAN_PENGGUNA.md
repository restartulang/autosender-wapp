# Panduan Pengguna (User Guide) - Autosender WAPP

**Autosender WAPP** adalah aplikasi otomasi pengiriman sandi cuaca (METAR, SPECI, SYNOP, TAFOR) yang dikembangkan untuk Stasiun Meteorologi Pattimura Ambon. Aplikasi ini menggunakan antarmuka grafis (GUI) modern dan terintegrasi dengan bot otomatis (Playwright) untuk mengirim data langsung ke CMSS/BMKGSoft.

---

## 1. Persiapan dan Login Pertama (Setup)

Saat pertama kali aplikasi dijalankan, Anda mungkin perlu mengatur kredensial (Username & Password) untuk BMKGSoft.
1. Klik menu **Pengaturan/Setup** di aplikasi.
2. Masukkan **Username** dan **Password** BMKGSoft Anda pada kotak yang disediakan. (Kotak input kini sudah disesuaikan agar lebih proporsional).
3. Anda dapat menekan **Test Koneksi** untuk memverifikasi apakah akun tersebut bisa digunakan untuk *login* ke server.
4. Klik **Simpan Credentials** untuk menyimpan secara aman ke dalam sistem lokal.

> [!NOTE]
> Bot otomatis tidak akan bisa mengirimkan sandi jika kredensial belum diatur dengan benar.

---

## 2. Antarmuka Utama (Dashboard)

Jendela utama aplikasi terdiri dari beberapa bagian responsif yang akan menyesuaikan dengan otomatis ketika Anda membukanya di monitor besar:
- **Header:** Menampilkan status sinkronisasi waktu (NTP Status) di pojok kanan atas.
- **Sidebar (Kiri):** Panel navigasi tersembunyi yang dapat dibuka dengan mengklik ikon *hamburger* di pojok kiri atas.
- **Input Panel (Kiri Tengah):** Tempat di mana Anda akan menempelkan (paste) sandi mentah dari WAPP/aplikasi sumber, yang kemudian akan di-parsing oleh sistem.
- **Queue Panel (Kanan Tengah):** Menampilkan daftar antrean pengiriman dan riwayat transmisi.
- **Dashboard Cards (Atas Kanan):** Menampilkan statistik ringkas (Jumlah antrean, berhasil hari ini, dan gagal/batal).

---

## 3. Cara Mengirim Sandi

1. **Input Sandi**: Masukkan (Paste) sandi cuaca pada kotak teks di **Input Panel**. 
2. Sistem akan otomatis mendeteksi tipe sandi (METAR, SYNOP, dll) beserta **Target Waktu UTC** berdasarkan isi sandi tersebut.
3. Klik tombol **Jadwalkan Pengiriman** (Atau tombol serupa).
4. Sandi akan masuk ke dalam **Daftar Antrean (Sedang Antre)** pada Panel Kanan.
5. Hitung mundur (countdown) akan berjalan secara *real-time*. Pada saat waktu target UTC mendekat dan waktu NTP terkonfirmasi akurat, bot akan bekerja di latar belakang (tanpa membuka jendela peramban) untuk masuk dan mengirimkan sandi tersebut.

---

## 4. Memantau Status & Riwayat (Queue Panel)

Panel kanan terdiri dari 2 tab utama:

### A. Tab "SEDANG ANTRE"
- Menampilkan semua sandi yang sedang menunggu waktu pengiriman.
- Menampilkan hitung mundur (countdown) presisi tinggi hingga waktu eksekusi tiba.
- Anda dapat membatalkan pengiriman dengan menekan tombol **( ✕ )** pada kolom AKSI sebelum waktu pengiriman tiba.

### B. Tab "RIWAYAT PENGIRIMAN"
- Menampilkan status keberhasilan seluruh pengiriman (Berhasil, Gagal, Dibatalkan).
- **Filter Tanggal:** Anda bisa menggunakan fitur kalender untuk melihat riwayat pada hari tertentu (misal: "Hari Ini", "Kemarin", dll). 
  > [!TIP]
  > Filter tanggal ini telah dioptimalkan agar akurat mendeteksi rentang waktu UTC berdasarkan hari lokal yang Anda pilih.
- Jika ada sandi yang **Gagal** terkirim, Anda bisa menekan tombol **( ↻ )** (Retry) di kolom aksi untuk mengulang kembali pengiriman sandi tersebut dari awal.
- Tekan tombol **( 👁 )** (View) untuk melihat rincian error, log, atau teks mentah dari sandi.

---

## 5. Fitur Keamanan dan Optimalisasi Sistem

- **Akurasi Waktu (NTP Sync):** Aplikasi selalu mencocokkan waktu sistem dengan standar waktu dunia (NTP Server). Bot hanya akan mengeksekusi pengiriman bila waktu tervalidasi sinkron dan aman.
- **Auto-Retry Cerdas:** Jika koneksi internet Anda tiba-tiba terputus sesaat, atau server mengalami *timeout*, sistem bot (Playwright) akan secara otomatis menunda sebentar dan mencoba melakukan pengiriman ulang di latar belakang.
- **Pembersihan Memori:** Aplikasi telah dibekali sistem pelacak "Zombie Chrome" yang akan membersihkan sisa memori peramban *headless* setiap kali aplikasi dijalankan. 

---

*Panduan ini berlaku untuk versi terbaru aplikasi Autosender WAPP V.2.1.*

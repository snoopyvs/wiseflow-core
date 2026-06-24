# WiseFlow - Logistics Route Optimization Platform

WiseFlow adalah platform berbasis web untuk mengoptimalkan rute logistik dan pengiriman barang menggunakan pendekatan *Capacitated Vehicle Routing Problem* (CVRP). Platform ini dirancang untuk menyelesaikan masalah pencarian rute terpendek dan termurah bagi armada truk yang memiliki keterbatasan kapasitas angkut.

## 🚀 Fitur Utama
1. **Interactive Map Interface**: Dibangun di atas peta *OpenStreetMap* dan *Leaflet.js*, memungkinkan pengguna memilih titik tujuan dan melihat animasi *routing* mengikuti jalan raya asli.
2. **Dynamic Constraints**: Validasi real-time untuk pembatasan berat (*capacity limit*) berdasarkan profil armada (*Vehicle Profile*).
3. **Multi-Objective Optimization**: Tiga pilihan mode algoritma:
   - 🍃 **Eco-Mode**: Meminimalkan biaya bensin (Rp). Memperhitungkan berat muatan truk secara dinamis (truk penuh lebih boros dari truk kosong).
   - ⚡ **Express Mode**: Meminimalkan jarak tempuh (km) murni tanpa peduli beban biaya.
   - ⚖️ **Balanced Mode**: Mengkombinasikan penghematan bensin dan waktu tempuh.
4. **Real Road Geometry via OSRM**: Kalkulasi lintasan tidak menggunakan garis lurus fiktif, melainkan menggunakan API *Open Source Routing Machine* (OSRM) yang menghitung belokan, arah jalan, dan bentuk aspal asli.

---

## 🧠 Algoritma & Logika Pencarian Rute (CVRP)

Dosen/Penguji seringkali berfokus pada **"Bagaimana sistem ini mendapatkan rute dan hasil yang optimal?"**. 
WiseFlow menggunakan **Algoritma A* (A-Star) Search** yang dimodifikasi untuk menyelesaikan CVRP (*Capacitated Vehicle Routing Problem*). 

Berikut adalah bongkar-mesin dari logika yang berjalan di file `src/ai_optimizer.py`:

### 1. Representasi State (Kondisi Saat Ini)
Karena ini adalah masalah CVRP (bukan sekadar cari jalan dari A ke B), algoritma A* tidak mencari rute di peta jalanan secara langsung, melainkan mengeksplorasi pohon kemungkinan urutan pengiriman (*state space tree*).

Setiap *node* (titik) dalam pohon pencarian A* menyimpan *State* berikut:
*   `f_cost`: Total estimasi biaya ($f(n) = g(n) + h(n)$).
*   `g_cost`: Biaya nyata yang sudah dihabiskan dari Depot sampai ke titik saat ini.
*   `current_node`: Lokasi truk saat ini berada.
*   `unvisited_tuple`: Kumpulan lokasi tujuan yang *belum* dikirim barangnya.
*   `current_load`: Total berat barang (kg) yang sedang dibawa truk saat ini.
*   `path`: Rekam jejak urutan rute yang sudah dilewati.

### 2. Aturan Transisi (Langkah yang Boleh Diambil)
Dari satu titik (misal Node A), truk memiliki dua pilihan keputusan (*action*):
1.  **Drop Barang ke Titik Tujuan Baru**: Truk boleh pergi ke tujuan selanjutnya **HANYA JIKA** total barang yang akan dikirim (beban saat ini + beban titik tujuan) **TIDAK MELEBIHI** kapasitas maksimal truk (`capacity_kg`).
2.  **Pulang ke Depot (Reload)**: Jika barang terlalu berat, truk boleh pulang ke Depot (Node 0). Saat sampai di Depot, `current_load` akan direset menjadi `0`, dan truk siap mengantar sisa tujuan lainnya. Algoritma akan menghitung ini sebagai perjalanan ekstra bolak-balik.

### 3. Cost Function / Biaya Real ($g(n)$)
Algoritma ini tidak statis. Biaya perjalanan dihitung sangat dinamis berdasarkan Mode Operasi yang dipilih pengguna:

*   **Jarak Asli (Haversine)**: Jarak antar node dihitung menggunakan rumus bola bumi (Haversine).
*   **Dinamika Bensin (Eco-Mode)**: Jika truk penuh (100% load), efisiensi bensin (`km/L`) akan otomatis dikurangi hingga **30% lebih boros** dibanding truk kosong. Jadi, truk yang berjalan kosong sejauh 10km akan lebih murah daripada truk bermuatan penuh sejauh 10km. Cost $g(n)$ diisi dengan nominal Rupiah harga bensin.

### 4. Heuristic Function ($h(n)$)
Agar algoritma A* berjalan cepat dan tidak mengeksplorasi cabang yang bodoh (seperti *Dijkstra/Breadth-First Search* murni), WiseFlow menggunakan fungsi Heuristik.
*   **Logika Heuristik**: *Cost* dari posisi truk saat ini menuju ke lokasi *unvisited* (belum dikunjungi) yang **paling dekat**.
*   **Sifat Admissible**: Nilai ini dijamin *admissible* (tidak pernah melebih-lebihkan biaya asli) karena jarak ke tetangga terdekat adalah batas bawah absolut dari sisa perjalanan yang harus ditempuh. Ini menjamin A* pasti menemukan rute paling optimal (solusi *optimal-guaranteed*).

### 5. Pruning (Pemangkasan Cabang)
Untuk menghindari *Out of Memory* saat jumlah rute banyak, sistem menggunakan *dictionary* `best_g`. Jika algoritma menemukan sebuah jalan ke *State* (posisi yang sama, sisa tujuan yang sama, muatan yang sama) namun dengan *cost* yang lebih mahal dari yang pernah ditemukan sebelumnya, cabang perhitungan itu akan langsung di-*pruning* (dibuang).

---

## 🛠 Alur Kerja Sistem (System Workflow)

1. **Pengguna Memasukkan Data (Frontend)**
   - Pengguna memilih truk. Frontend langsung mengambil atribut kapasitas dan BBM dari *database*.
   - Pengguna mengetik alamat. *Nominatim API* mengubah teks alamat menjadi koordinat *Latitude/Longitude*.
   - Saat pengguna menekan `+`, Javascript memvalidasi apakah beban tunggal melebihi kapasitas truk. Jika ya, diblokir.
2. **Kalkulasi Optimasi (Backend)**
   - Frontend mengirim susunan koordinat dan beban ke Backend Flask (`/api/optimize`).
   - Python memproses matriks jarak *all-to-all* antar koordinat.
   - Algoritma **A* CVRP** `solve_routing()` dieksekusi untuk mencari urutan paling murah/pendek berdasarkan mode yang diminta (Eco/Express/Balanced).
   - Setelah urutan optimal didapat (misal: Depot -> C -> B -> Depot -> A), Backend mengirim data ini kembali.
3. **Visualisasi Peta (Frontend)**
   - Frontend menerima urutan lokasi optimal.
   - Melakukan *request* berantai ke API *OSRM Route* untuk menggambar garis aspal per lintasan.
   - Peta dirender. Rute digambar selang-seling menggunakan palet warna berbeda agar tumpukan jalan raya terlihat natural. Garis rute diikat dengan *Hover Tooltip* berisi urutan.

## 💻 Tech Stack
- **Frontend**: HTML5, Vanilla JavaScript, TailwindCSS, Leaflet.js (Map Rendering).
- **Backend**: Python 3, Flask.
- **Algorithms**: A* Search, Haversine Distance Calculation.
- **External APIs**: 
  - OpenStreetMap (Map Tiles)
  - Nominatim (Geocoding / Pencarian Alamat)
  - OSRM (Road Geometry Routing)

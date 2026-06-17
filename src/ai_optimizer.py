import math
import heapq
import time

def haversine_distance(coord1, coord2):
    """
    Menghitung jarak lurus (straight-line) antar dua koordinat menggunakan rumus Haversine.
    coord format: (latitude, longitude)
    Output dalam kilometer (km).
    """
    R = 6371.0 # Radius bumi dalam kilometer
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def create_distance_matrix(locations, mode="Balanced"):
    """
    Membuat matriks jarak antar semua titik lokasi yang ada.
    locations: list of dict, misal: [{'id': 'depot', 'lat': -6.2, 'lon': 106.8}, ...]
    """
    n = len(locations)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                base_dist = haversine_distance(
                    (locations[i]['lat'], locations[i].get('lng', locations[i].get('lon'))),
                    (locations[j]['lat'], locations[j].get('lng', locations[j].get('lon')))
                )
                
                # LOGIKA BARU: TOL vs JALAN BIASA (Multi-Objective Optimization)
                # Kita gunakan pseudo-random untuk menentukan apakah jalur ini ada Tol-nya atau tidak.
                hash_val = abs(math.sin(locations[i]['lat'] * locations[j].get('lng', locations[j].get('lon'))))
                is_toll = hash_val > 0.4  # 60% peluang jalur ini adalah jalan Tol
                
                if is_toll:
                    speed_kmh = 80.0  # Kecepatan tinggi
                    toll_fee = base_dist * 1000  # Ada biaya tol Rp 1000 / km
                else:
                    speed_kmh = 40.0  # Kecepatan lambat (jalan biasa/macet)
                    toll_fee = 0.0    # Gratis
                    
                fuel_cost = base_dist * 1500  # Biaya bensin dasar Rp 1500 / km
                
                # Kalkulasi Waktu (Jam) dan Biaya (Rupiah)
                time_hours = base_dist / speed_kmh
                total_cost_rp = fuel_cost + toll_fee
                
                if mode == "Eco":
                    # ECO: Murni mencari BIAYA TERMURAH (Rupiah). 
                    # Algoritma akan otomatis menghindari jalan Tol karena ada toll_fee,
                    # walau akibatnya waktu tempuh (time_hours) jadi lebih lama.
                    matrix[i][j] = total_cost_rp
                    
                elif mode == "Express":
                    # EXPRESS: Murni mencari WAKTU TERCEPAT (Jam).
                    # Algoritma akan mencari jalan Tol (80km/h) walau biayanya mahal.
                    # Kita kalikan 10.000 agar angkanya tidak terlalu kecil untuk dihitung A*
                    matrix[i][j] = time_hours * 10000 
                    
                else:
                    # BALANCED: Menggabungkan Biaya dan Waktu.
                    # Asumsi: 1 jam waktu supir berharga Rp 50.000
                    matrix[i][j] = total_cost_rp + (time_hours * 50000)
                    
    return matrix

def solve_routing(locations, use_heuristic=True, mode="Balanced"):
    """
    Fungsi utama untuk mencari rute terpendek mengunjungi semua tujuan (TSP problem).
    Jika use_heuristic = True  -> Menggunakan Algoritma A*
    Jika use_heuristic = False -> Menggunakan Algoritma Dijkstra (Uniform Cost Search)
    """
    start_time = time.time()
    nodes_expanded = 0
    
    # Buat matriks jarak antar titik biar komputasi lebih cepat (tidak ngitung berulang-ulang)
    dist_matrix = create_distance_matrix(locations, mode)
    n = len(locations)
    
    # State direpresentasikan sebagai tuple: (current_node_index, unvisited_nodes_tuple)
    # Tujuan kita: unvisited_nodes_tuple menjadi kosong.
    
    # Inisialisasi State Awal
    initial_unvisited = tuple(i for i in range(1, n)) # Depot diasumsikan index 0
    
    # Priority Queue untuk nyimpan antrean State yang mau dicek.
    # Format antrean: (f_cost, g_cost, current_node, unvisited_tuple, path_history)
    pq = []
    
    # g(n) awal adalah 0 karena kita baru mulai dari depot
    heapq.heappush(pq, (0.0, 0.0, 0, initial_unvisited, [0]))
    
    # Dictionary buat nyimpen cost terkecil untuk suatu state biar gak ngecek ulang state yang sama
    best_g = {}
    best_g[(0, initial_unvisited)] = 0.0
    
    best_path = []
    min_cost = float('inf')
    
    while pq:
        # Ambil state dengan f_cost paling kecil dari antrean
        f_cost, g_cost, curr, unvisited, path = heapq.heappop(pq)
        nodes_expanded += 1
        
        # Jika semua titik sudah dikunjungi (unvisited kosong)
        if not unvisited:
            # Karena ini logistik, mungkin kita perlu hitung jarak kembali ke depot (index 0)
            # Di sini kita asumsikan rute selesai di titik terakhir (tidak wajib balik depot).
            if g_cost < min_cost:
                min_cost = g_cost
                best_path = path
            break # Berhenti karena algoritma A*/Dijkstra pasti nemu yang paling optimal pertama kali
            
        # Jika bukan yang tercepat untuk state ini, skip aja (Pruning)
        if g_cost > best_g.get((curr, unvisited), float('inf')):
            continue
            
        # Ekspansi / cari cabang ke titik selanjutnya
        for nxt in unvisited:
            # Hitung jarak/cost riil dari titik saat ini ke titik berikutnya
            # (Cost ini sudah dimodifikasi oleh Mode Operasi di fungsi create_distance_matrix)
            step_cost = dist_matrix[curr][nxt]
            
            # Perhitungan g(n) baru
            new_g = g_cost + step_cost
            
            # Bikin state unvisited baru (hapus titik yang barusan dikunjungi)
            new_unvisited = tuple(u for u in unvisited if u != nxt)
            
            # Jika cost baru lebih kecil dari yang pernah dicatat, masukan ke antrean
            if new_g < best_g.get((nxt, new_unvisited), float('inf')):
                best_g[(nxt, new_unvisited)] = new_g
                
                # PERHITUNGAN HEURISTIK h(n) UNTUK A*
                h_cost = 0.0
                if use_heuristic and new_unvisited:
                    # Rumus Heuristik Admissible (Tidak boleh melebihi cost asli):
                    # Kita cari jarak lurus (Haversine) terdekat ke titik yang belum dikunjungi.
                    # Karena bobot (g_cost) sekarang berbeda tiap mode, h_cost juga HARUS menyesuaikan unitnya!
                    nearest_dist_km = float('inf')
                    for u in new_unvisited:
                        # Hitung haversine murni
                        d = haversine_distance(
                            (locations[nxt]['lat'], locations[nxt].get('lng', locations[nxt].get('lon'))),
                            (locations[u]['lat'], locations[u].get('lng', locations[u].get('lon')))
                        )
                        if d < nearest_dist_km: nearest_dist_km = d
                        
                    if mode == "Eco":
                        # Di Eco, cost adalah Rupiah. Cost minimal per km adalah 1500 (tanpa tol).
                        h_cost = nearest_dist_km * 1500
                    elif mode == "Express":
                        # Di Express, cost adalah Waktu * 10000. Kecepatan maksimal adalah 80km/h.
                        # Waktu minimal = Jarak / 80.
                        h_cost = (nearest_dist_km / 80.0) * 10000
                    else: # Balanced
                        # Cost minimal = Bensin tanpa tol + Waktu ngebut (Jarak/80 * 50000)
                        h_cost = nearest_dist_km * 1500 + ((nearest_dist_km / 80.0) * 50000)
                
                # Fungsi f(n) = g(n) + h(n)
                # Jika Dijkstra (use_heuristic=False), maka h_cost = 0, sehingga f(n) = g(n) (Uniform Cost Search)
                new_f = new_g + h_cost
                
                # Masukkan state baru ke Priority Queue
                new_path = list(path)
                new_path.append(nxt)
                heapq.heappush(pq, (new_f, new_g, nxt, new_unvisited, new_path))
                
    execution_time_ms = (time.time() - start_time) * 1000
    
    # Susun ulang data rute hasil akhir
    route_details = []
    for idx in best_path:
        route_details.append(locations[idx])
        
    # Untuk display frontend, kita tetep butuh hitung Jarak Asli (km) dari best_path
    total_real_distance = 0.0
    for i in range(len(best_path) - 1):
        idx_a = best_path[i]
        idx_b = best_path[i+1]
        total_real_distance += haversine_distance(
            (locations[idx_a]['lat'], locations[idx_a].get('lng', locations[idx_a].get('lon'))),
            (locations[idx_b]['lat'], locations[idx_b].get('lng', locations[idx_b].get('lon')))
        )
        
    return {
        "algorithm": "A*" if use_heuristic else "Dijkstra",
        "route_indices": best_path,
        "route_locations": route_details,
        "total_distance_km": round(total_real_distance, 2),
        "nodes_expanded": nodes_expanded,
        "execution_time_ms": round(execution_time_ms, 2)
    }

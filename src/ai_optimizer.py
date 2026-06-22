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

def create_distance_matrix(locations):
    """
    Membuat matriks jarak (dalam km) antar semua titik lokasi yang ada.
    """
    n = len(locations)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = haversine_distance(
                    (locations[i]['lat'], locations[i].get('lng', locations[i].get('lon'))),
                    (locations[j]['lat'], locations[j].get('lng', locations[j].get('lon')))
                )
    return matrix

def calculate_fuel_cost(distance_km, current_load_kg, max_capacity_kg, base_efficiency_kml):
    """
    Menghitung biaya bensin berdasarkan beban dinamis.
    Truk penuh (100% load) akan 30% lebih boros bensin dari truk kosong.
    """
    if max_capacity_kg <= 0 or base_efficiency_kml <= 0:
        return 0.0
        
    # Pengurangan efisiensi berbanding lurus dengan load (max -30%)
    load_ratio = min(current_load_kg / max_capacity_kg, 1.0)
    efficiency_drop = 0.3 * load_ratio
    actual_efficiency_kml = base_efficiency_kml * (1.0 - efficiency_drop)
    
    # Harga bensin (contoh: Biosolar Rp 6.800/L)
    FUEL_PRICE = 6800.0
    
    liters_used = distance_km / actual_efficiency_kml
    return liters_used * FUEL_PRICE

def solve_routing(locations, capacity_kg, base_fuel_efficiency_kml, use_heuristic=True, mode="Balanced"):
    """
    Menyelesaikan Capacitated Vehicle Routing Problem (CVRP)
    State: (current_node, unvisited_tuple, current_load)
    """
    start_time = time.time()
    nodes_expanded = 0
    
    dist_matrix = create_distance_matrix(locations)
    n = len(locations)
    
    # Ambil data demand tiap lokasi (asumsi index 0 adalah depot dengan demand 0)
    demands = [float(loc.get('demand', 0)) for loc in locations]
    
    # Validasi awal: Jika ada 1 barang > kapasitas truk, otomatis error dari API
    # State awal: (cost_g, current_node, unvisited_tuple, current_load, path_history, total_distance, total_fuel_cost)
    initial_unvisited = tuple(i for i in range(1, n))
    
    # Priority queue format: (f_cost, g_cost, current_node, unvisited_tuple, current_load, path, total_dist, total_fuel)
    pq = []
    heapq.heappush(pq, (0.0, 0.0, 0, initial_unvisited, 0.0, [0], 0.0, 0.0))
    
    best_g = {}
    best_g[(0, initial_unvisited, 0.0)] = 0.0
    
    best_path = []
    min_cost = float('inf')
    final_distance = 0.0
    final_fuel = 0.0
    
    while pq:
        f_cost, g_cost, curr, unvisited, current_load, path, total_dist, total_fuel = heapq.heappop(pq)
        nodes_expanded += 1
        
        # Goal Check: Jika semua node sudah dikunjungi
        if not unvisited:
            # Opsional: Paksa balik ke depot di akhir?
            # CVRP biasanya wajib balik ke depot. Kita tambahkan perjalanan pulang ke depot (node 0)
            if curr != 0:
                dist_to_depot = dist_matrix[curr][0]
                fuel_to_depot = calculate_fuel_cost(dist_to_depot, current_load, capacity_kg, base_fuel_efficiency_kml)
                
                step_cost = 0.0
                if mode == "Eco": step_cost = fuel_to_depot
                elif mode == "Express": step_cost = dist_to_depot
                else: step_cost = fuel_to_depot + (dist_to_depot * 2000) # Balanced
                
                g_cost += step_cost
                total_dist += dist_to_depot
                total_fuel += fuel_to_depot
                path = list(path)
                path.append(0)
            
            if g_cost < min_cost:
                min_cost = g_cost
                best_path = path
                final_distance = total_dist
                final_fuel = total_fuel
            break # Ketemu solusi optimal
            
        # Pruning
        if g_cost > best_g.get((curr, unvisited, current_load), float('inf')):
            continue
            
        # Aksi 1: Kembali ke Depot (hanya relevan jika kita tidak di depot dan muatan > 0)
        if curr != 0 and current_load > 0:
            dist_to_depot = dist_matrix[curr][0]
            fuel_to_depot = calculate_fuel_cost(dist_to_depot, current_load, capacity_kg, base_fuel_efficiency_kml)
            
            step_cost = 0.0
            if mode == "Eco": step_cost = fuel_to_depot
            elif mode == "Express": step_cost = dist_to_depot
            else: step_cost = fuel_to_depot + (dist_to_depot * 2000) # Balanced
            
            new_g = g_cost + step_cost
            new_state_key = (0, unvisited, 0.0) # Load reset ke 0
            
            if new_g < best_g.get(new_state_key, float('inf')):
                best_g[new_state_key] = new_g
                new_path = list(path)
                new_path.append(0)
                
                # Heuristic: jarak dari depot ke nearest unvisited
                h_cost = 0.0
                if use_heuristic and unvisited:
                    nearest = min(dist_matrix[0][u] for u in unvisited)
                    if mode == "Eco":
                        # Truk asumsikan kosong
                        h_cost = calculate_fuel_cost(nearest, 0.0, capacity_kg, base_fuel_efficiency_kml)
                    elif mode == "Express":
                        h_cost = nearest
                    else:
                        h_cost = calculate_fuel_cost(nearest, 0.0, capacity_kg, base_fuel_efficiency_kml) + (nearest * 2000)
                
                heapq.heappush(pq, (new_g + h_cost, new_g, 0, unvisited, 0.0, new_path, total_dist + dist_to_depot, total_fuel + fuel_to_depot))

        # Aksi 2: Lanjut ke tujuan berikutnya
        for nxt in unvisited:
            demand_nxt = demands[nxt]
            
            # CEK CONSTRAINT KAPASITAS
            if current_load + demand_nxt > capacity_kg:
                # Tidak bisa langsung pergi, skip (Aksi 1 akan handle perjalanan ke depot)
                continue
                
            dist_to_nxt = dist_matrix[curr][nxt]
            fuel_to_nxt = calculate_fuel_cost(dist_to_nxt, current_load, capacity_kg, base_fuel_efficiency_kml)
            
            step_cost = 0.0
            if mode == "Eco": step_cost = fuel_to_nxt
            elif mode == "Express": step_cost = dist_to_nxt
            else: step_cost = fuel_to_nxt + (dist_to_nxt * 2000)
            
            new_g = g_cost + step_cost
            new_load = current_load + demand_nxt
            new_unvisited = tuple(u for u in unvisited if u != nxt)
            
            new_state_key = (nxt, new_unvisited, new_load)
            
            if new_g < best_g.get(new_state_key, float('inf')):
                best_g[new_state_key] = new_g
                new_path = list(path)
                new_path.append(nxt)
                
                h_cost = 0.0
                if use_heuristic and new_unvisited:
                    nearest = min(dist_matrix[nxt][u] for u in new_unvisited)
                    if mode == "Eco":
                        h_cost = calculate_fuel_cost(nearest, new_load, capacity_kg, base_fuel_efficiency_kml)
                    elif mode == "Express":
                        h_cost = nearest
                    else:
                        h_cost = calculate_fuel_cost(nearest, new_load, capacity_kg, base_fuel_efficiency_kml) + (nearest * 2000)
                
                heapq.heappush(pq, (new_g + h_cost, new_g, nxt, new_unvisited, new_load, new_path, total_dist + dist_to_nxt, total_fuel + fuel_to_nxt))

    execution_time_ms = (time.time() - start_time) * 1000
    
    # Susun ulang data rute hasil akhir
    route_details = []
    if best_path:
        for idx in best_path:
            # Karena bisa mampir depot berkali-kali, kita butuh clone dict lokasinya
            loc_data = locations[idx].copy()
            route_details.append(loc_data)
            
    return {
        "algorithm": "A*" if use_heuristic else "Dijkstra",
        "route_indices": best_path,
        "route_locations": route_details,
        "total_distance_km": round(final_distance, 2),
        "total_fuel_cost_rp": round(final_fuel, 2),
        "nodes_expanded": nodes_expanded,
        "execution_time_ms": round(execution_time_ms, 2)
    }

# WiseFlow - Logistics Route Optimization Platform

WiseFlow is a web-based platform for optimizing logistics and delivery routes using the *Capacitated Vehicle Routing Problem* (CVRP) approach. This platform is designed to solve the problem of finding the shortest and cheapest routes for a fleet of trucks with limited carrying capacities.

## 🚀 Key Features
1. **Interactive Map Interface**: Built on *OpenStreetMap* and *Leaflet.js*, allowing users to select destination points and view routing animations following actual road networks.
2. **Dynamic Constraints**: Real-time validation for weight limits (capacity limits) based on the selected *Vehicle Profile*.
3. **Multi-Objective Optimization**: Three algorithmic modes:
   - 🍃 **Eco-Mode**: Minimizes fuel costs (IDR). Dynamically accounts for truck load weight (a fully loaded truck consumes more fuel than an empty one).
   - ⚡ **Express Mode**: Strictly minimizes travel distance (km) without factoring in costs.
   - ⚖️ **Balanced Mode**: Finds the optimal balance between fuel savings and travel distance.
4. **Real Road Geometry via OSRM**: Calculates paths using the *Open Source Routing Machine* (OSRM) API, factoring in actual road shapes, turns, and real-world asphalt routes rather than fictional straight lines.

---

## 🧠 Algorithm & Routing Logic (CVRP)

For academic or technical evaluation, understanding **"How does the system obtain optimal routes?"** is crucial.
WiseFlow utilizes a modified **A* (A-Star) Search Algorithm** tailored to solve the CVRP.

Here is an under-the-hood breakdown of the logic running in `src/ai_optimizer.py`:

### 1. State Representation
Since this is a CVRP (not just simple A-to-B routing), the A* algorithm does not search directly on the street map. Instead, it explores a *state space tree* of possible delivery sequences.

Each *node* in the A* search tree holds the following *State*:
*   `f_cost`: Total estimated cost ($f(n) = g(n) + h(n)$).
*   `g_cost`: The actual cost spent from the Depot to the current point.
*   `current_node`: The truck's current location.
*   `unvisited_tuple`: A set of destination locations that have *not* yet been delivered to.
*   `current_load`: The total weight of goods (kg) currently carried by the truck.
*   `path`: The historical sequence of the route taken so far.

### 2. Transition Rules (Allowed Actions)
From any point (e.g., Node A), the truck has two possible actions:
1.  **Drop Goods at a New Destination**: The truck may proceed to the next destination **ONLY IF** the total goods to be delivered (current load + destination demand) **DOES NOT EXCEED** the truck's maximum capacity (`capacity_kg`).
2.  **Return to Depot (Reload)**: If the goods are too heavy, the truck may return to the Depot (Node 0). Upon arriving at the Depot, the `current_load` is reset to `0`, and the truck is ready to deliver the remaining destinations. The algorithm calculates this as extra round-trip travel.

### 3. Real Cost Function ($g(n)$)
The journey cost is calculated dynamically based on the user's selected Operating Mode:

*   **Actual Distance (Haversine)**: Distance between nodes is calculated using the Haversine spherical formula.
*   **Fuel Dynamics (Eco-Mode)**: If a truck is fully loaded (100% capacity), fuel efficiency (`km/L`) automatically drops, making it up to **30% more inefficient** compared to an empty truck. Thus, an empty truck traveling 10km will incur a lower cost than a fully loaded truck traveling 10km. The $g(n)$ cost is represented in real currency (IDR) for fuel prices.

### 4. Heuristic Function ($h(n)$)
To ensure the A* algorithm runs efficiently and avoids exploring suboptimal branches (unlike pure Dijkstra/BFS), WiseFlow employs a Heuristic function.
*   **Heuristic Logic**: The cost from the truck's current position to the **nearest unvisited location**.
*   **Admissibility**: This value is guaranteed to be *admissible* (it never overestimates the true cost) because the distance to the nearest neighbor is the absolute lower bound of the remaining journey. This guarantees that A* will find the mathematically optimal route.

### 5. Pruning
To prevent *Out of Memory* errors when the number of routes is large, the system maintains a `best_g` dictionary. If the algorithm discovers a path to a specific *State* (same position, same remaining destinations, same load) but with a higher cost than previously found, that computational branch is immediately pruned (discarded).

---

## 🛠 System Workflow

1. **User Input (Frontend)**
   - The user selects a truck. The frontend fetches the capacity and fuel attributes from the *database*.
   - The user types an address. The *Nominatim API* converts the text into *Latitude/Longitude* coordinates.
   - When the user clicks `+`, JavaScript validates if the single load exceeds the truck's capacity. If it does, the addition is blocked.
2. **Optimization Calculation (Backend)**
   - The frontend sends the array of coordinates and demands to the Flask Backend (`/api/optimize`).
   - Python processes the *all-to-all* distance matrix between coordinates.
   - The **A* CVRP** `solve_routing()` algorithm executes to find the cheapest/shortest sequence based on the requested mode.
   - Once the optimal sequence is found (e.g., Depot -> C -> B -> Depot -> A), the Backend returns this data.
3. **Map Visualization (Frontend)**
   - The frontend receives the optimal location sequence.
   - It makes sequential requests to the *OSRM Route API* to draw actual road geometries per path segment.
   - The map is rendered. Routes are drawn with interleaved dash patterns and colors to ensure overlapping roads look natural. Route lines are bound with *Hover Tooltips* indicating the sequence.

## 💻 Tech Stack
- **Frontend**: HTML5, Vanilla JavaScript, TailwindCSS, Leaflet.js (Map Rendering).
- **Backend**: Python 3, Flask.
- **Algorithms**: A* Search, Haversine Distance Calculation.
- **External APIs**: 
  - OpenStreetMap (Map Tiles)
  - Nominatim (Geocoding / Address Search)
  - OSRM (Road Geometry Routing)

---

## 🏃 Local Setup & Demo Guide

For team members or evaluators who want to run this application locally, follow these steps:

### Prerequisites
Ensure your machine has **Python (version 3.8 or higher)** and **Git** installed.

### Installation Steps
1. **Clone the Repository**
   Open your terminal/CMD and run:
   ```bash
   git clone https://github.com/snoopyvs/wiseflow-core.git
   cd wiseflow-core
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # Windows users: venv\Scripts\activate
   # Mac/Linux users: source venv/bin/activate
   ```

3. **Install Dependencies**
   Install all required Python libraries (especially Flask):
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables (.env)**
   Create a new file named `.env` in the root folder (`wiseflow-core/`) and add the following Flask credential:
   ```env
   SECRET_KEY=tugas-ai-wiseflow-rahasia
   ```

5. **Initialize the Database**
   Before running the app, initialize the SQLite database and populate it with dummy vehicle data:
   ```bash
   python init_db.py
   ```

6. **Run the Application**
   Start the Flask backend server:
   ```bash
   python -m src.app
   ```

7. **Open in Browser**
   Open your web browser (Google Chrome is recommended) and navigate to:
   👉 **`http://127.0.0.1:5000`**

### Quick Demo Guide:
- Navigate directly to the **Optimizer** menu.
- Select a truck from the dropdown. (Try inputting a weight that exceeds this truck's capacity; the `+` button logic will automatically reject it!).
- Enter a *Starting Point* (e.g., "Jakarta").
- Enter several *Destinations* along with their load weights (e.g., "Bandung" 500kg, "Semarang" 1000kg).
- Select an *Operating Mode* (Eco / Express / Balanced).
- Click the **Generate Optimized Sequence** button.
- Wait for the A* Search process to complete in the backend. Once finished, the map will render real road routes, and the *Routing Timeline* at the bottom will display the optimal sequence of visits!

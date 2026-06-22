# 🗺️ RouteMaster — Map Navigation System

A Google Maps-like navigation system built with real Mumbai road network data using OpenStreetMap, OSMnx, NetworkX, and Folium.

## 📌 Project Overview

RouteMaster is a scalable map navigation system that demonstrates:
- Real road network loading from OpenStreetMap (Mumbai)
- Shortest path calculation using **Dijkstra's** and **A\*** algorithms
- Interactive map rendering in the browser (like Google Maps)
- Real-time traffic simulation and dynamic rerouting
- ETA calculation with congestion factors

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Road Network Data | OpenStreetMap via OSMnx |
| Pathfinding | NetworkX (Dijkstra, A*) |
| Map Rendering | Folium |
| Language | Python 3.9+ |

## 📦 Dependencies

```
osmnx
networkx
folium
pandas
numpy
shapely
geopandas
```

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/routemaster
cd routemaster
```

### 2. Install dependencies
```bash
pip3 install osmnx networkx folium
```

### 3. Run the application
```bash
python3 main.py
```

## 🚀 Execution Steps

1. Run `python3 main.py`
2. Wait for Mumbai road network to load (~30 seconds first time, cached after)
3. Select a **start location** from the Mumbai landmarks list
4. Select a **destination** from the list
5. Choose your routing algorithm (Dijkstra / A* / Compare Both)
6. The map opens automatically in your browser showing:
   - The route drawn on real Mumbai streets (blue = Dijkstra, green = A*)
   - Start (green) and end (red) markers
   - Traffic congestion markers (orange dots)
   - Info panel with distance, ETA, and traffic ETA

## 📁 Project Structure

```
routemaster/
├── main.py              # Entry point — user interaction + orchestration
├── routing_engine.py    # Dijkstra, A*, graph loading, route stats
├── map_visualizer.py    # Folium map rendering
├── traffic_engine.py    # Traffic simulation and rerouting logic
├── routemaster_map.html # Generated map output (opens in browser)
└── README.md
```

## 🏙️ Available Mumbai Landmarks

- CST Station
- Bandra Station
- Juhu Beach
- Gateway of India
- Dadar Station
- Andheri Station
- Worli Sea Link
- Haji Ali
- Marine Drive
- Powai Lake

## 🔗 GitHub Repository

> https://github.com/YOUR_USERNAME/routemaster

## 📚 Additional Details

- First run downloads ~10MB of Mumbai road network data (cached locally after)
- The map is saved as `routemaster_map.html` and opens in your default browser
- Traffic simulation uses time-of-day logic (peak hours: 8–11am, 5–9pm)
- A* uses the Haversine formula as its geographic heuristic
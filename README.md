<div align="center">


# RouteMaster

### Real-Time Map Navigation System — Mumbai


A Google Maps-style navigation system running **Dijkstra and A\*** on the real Mumbai road network.  
Not a simulation — actual shortest paths on actual streets.

**[Features](#-features) · [Installation](#-installation) · [Usage](#-usage) · [API](#-api-reference) · [Architecture](#-architecture) · [Algorithms](#-algorithm-details)**

---

</div>

## What is RouteMaster?

RouteMaster is a fully working map navigation system built on **real OpenStreetMap road data** for Mumbai. It downloads 3,200+ intersections and 8,500+ road segments, runs graph algorithms on them, and renders the result on an interactive Google Maps-style interface in the browser.

Built for the **System Design (Semester IV)** course — B.Tech CSE 2024–28, ITM Skills University.

---

## Features

- **Real road network** — Mumbai road graph downloaded live from OpenStreetMap via OSMnx
- **Dijkstra's algorithm** — guaranteed shortest path using a min-heap priority queue
- **A\* Search** — faster guided search using the Haversine distance heuristic
- **Compare mode** — run both algorithms at once and see them drawn side by side
- **Traffic simulation** — peak-hour congestion (1.8x–2.8x delay) based on actual time of day
- **Dynamic rerouting** — high-severity incidents trigger alternate route suggestions
- **Google Maps UI** — white sidebar panel, blue route line, start dot, destination pin
- **Satellite toggle** — switch between OpenStreetMap street view and Esri satellite imagery
- **Live traffic feed** — accident alerts, roadwork warnings, signal failures with timestamps
- **REST API** — clean JSON endpoint for route calculation, usable by any frontend

---

## Project Structure

```
routemaster/
├── app.py                 Flask web server + REST API
├── routing_engine.py      Dijkstra · A* · graph loading · ETA calculation
├── traffic_engine.py      Traffic simulation · congestion · rerouting logic
├── map_visualizer.py      Folium map rendering for terminal mode
├── main.py                Standalone terminal navigation interface
├── requirements.txt       Python dependencies
├── README.md              This file
└── templates/
    └── index.html         Google Maps-style single-page web UI
```

---

## Installation

### Requirements

- Python 3.9+
- pip
- Internet connection (for first-time road network download ~10 MB)

### 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/routemaster.git
cd routemaster
```

### 2 — Install dependencies

```bash
pip3 install flask osmnx networkx folium scikit-learn
```

Or using the requirements file:

```bash
pip3 install -r requirements.txt
```

### 3 — Start the server

```bash
python3 app.py
```

### 4 — Open in browser

```
http://127.0.0.1:5000
```

> **Note:** The first run downloads Mumbai's road network from OpenStreetMap — allow 30–60 seconds. Every run after that is instant because OSMnx caches the data locally.

---

## Usage

### Web App

1. Run `python3 app.py`
2. Go to `http://127.0.0.1:5000`
3. Pick a **start location** from the dropdown
4. Pick a **destination**
5. Choose **Dijkstra**, **A\* Search**, or **Compare**
6. Click **Get Directions**

The route draws on real Mumbai streets. The sidebar shows:

- Distance in km
- Free-flow ETA
- Traffic-adjusted ETA with congestion level badge
- Turn-by-turn steps
- Live incident feed

### Terminal Mode

```bash
python3 main.py
```

Select landmarks by number, pick an algorithm, and the route opens as `routemaster_map.html` in your browser.

---

## Available Landmarks

| # | Location | Lat | Lon |
|---|---|---|---|
| 1 | CST Station | 18.9398 | 72.8354 |
| 2 | Bandra Station | 19.0596 | 72.8397 |
| 3 | Juhu Beach | 19.0989 | 72.8267 |
| 4 | Gateway of India | 18.9220 | 72.8347 |
| 5 | Dadar Station | 19.0178 | 72.8478 |
| 6 | Andheri Station | 19.1197 | 72.8464 |
| 7 | Worli Sea Link | 19.0176 | 72.8152 |
| 8 | Haji Ali | 18.9827 | 72.8089 |
| 9 | Marine Drive | 18.9432 | 72.8236 |
| 10 | Powai Lake | 19.1197 | 72.9050 |

---

## API Reference

### `POST /api/route`

Calculate a route between two GPS coordinates.

**Request**

```json
{
  "start":     { "lat": 18.9398, "lon": 72.8354 },
  "end":       { "lat": 19.0989, "lon": 72.8267 },
  "algorithm": "dijkstra"
}
```

`algorithm` accepts: `dijkstra` · `astar` · `both`

**Response**

```json
{
  "status":    "ok",
  "algorithm": "Dijkstra",
  "coords":    [[18.940, 72.835], [18.951, 72.838], "..."],
  "stats": {
    "distance_km": 9.92,
    "eta_min":     19.8
  },
  "traffic": {
    "factor":           1.09,
    "eta_with_traffic": 21.7,
    "level":            "low",
    "updates": [
      { "message": "✅ Road clear",      "time": "14:36:45" },
      { "message": "🚦 Signal failure",  "time": "14:36:45" },
      { "message": "🚧 Road work ahead", "time": "14:36:45" }
    ]
  }
}
```

**Compare response** (when `algorithm: "both"`)

```json
{
  "status":    "ok",
  "algorithm": "both",
  "dijkstra":  { "coords": [...], "stats": { "distance_km": 9.92, "eta_min": 19.8 } },
  "astar":     { "coords": [...], "stats": { "distance_km": 9.92, "eta_min": 19.8 } },
  "traffic":   { "factor": 1.09, "eta_with_traffic": 21.7, "level": "low", "updates": [...] }
}
```

---

### `GET /api/landmarks`

Returns all available landmarks with coordinates.

```bash
curl http://127.0.0.1:5000/api/landmarks
```

```json
{
  "CST Station":      { "lat": 18.9398, "lon": 72.8354 },
  "Bandra Station":   { "lat": 19.0596, "lon": 72.8397 },
  "..."
}
```

---

## Algorithm Details

### Dijkstra's Algorithm

Expands nodes in order of increasing distance from the source using a min-heap. Explores roads in every direction until it reaches the destination. Guarantees the globally optimal shortest path.

```python
path = nx.shortest_path(G, origin_node, dest_node, weight='length')
```

Time complexity: `O((V + E) log V)`

### A\* Search

Adds a heuristic to Dijkstra — the Haversine straight-line distance to the destination. Instead of expanding in all directions, A\* prioritises roads that move closer to the destination. Visits fewer nodes, runs faster, produces the same optimal result.

```python
def heuristic(u, v):
    return haversine(
        G.nodes[u]['y'], G.nodes[u]['x'],
        G.nodes[v]['y'], G.nodes[v]['x']
    )

path = nx.astar_path(G, origin, dest, heuristic=heuristic, weight='length')
```

Time complexity: `O((V + E) log V)` worst case — significantly faster in practice.

### Comparison

| | Dijkstra | A\* |
|---|---|---|
| Result | Optimal | Optimal |
| Speed | Moderate | Faster |
| Heuristic | None | Haversine distance |
| Nodes explored | All reachable | Guided toward goal |
| Best use case | Unknown topology | Geographic routing |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                     CLIENTS                          │
│          Browser · Mobile App · External API         │
└───────────────────────┬──────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼──────────────────────────────┐
│               API GATEWAY + LOAD BALANCER            │
│          Auth · Rate limiting · Request routing      │
└────────┬──────────────┬───────────────┬──────────────┘
         │              │               │
    ┌────▼────┐   ┌──────▼──────┐  ┌───▼────────┐
    │   Map   │   │   Routing   │  │  Traffic   │
    │ Service │   │   Engine    │  │  Service   │
    │  Tiles  │   │ Dijkstra·A* │  │ Congestion │
    └────┬────┘   └──────┬──────┘  └───┬────────┘
         │               │              │
┌────────▼───────────────▼──────────────▼──────────────┐
│                      DATA LAYER                      │
│         PostGIS · Graph Store · Redis · User DB      │
└──────────────────────────────────────────────────────┘
```

### Module responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | HTTP server, request routing, JSON serialisation |
| `routing_engine.py` | Graph loading, Dijkstra, A\*, ETA calculation |
| `traffic_engine.py` | Congestion factors, incident events, rerouting decisions |
| `map_visualizer.py` | Folium map creation, route rendering, marker placement |
| `index.html` | Leaflet map, sidebar UI, fetch API calls, route drawing |

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Road data | OpenStreetMap via OSMnx | Free, real-world, no API key |
| Graph algorithms | NetworkX | Production Dijkstra + A\* built in |
| Map rendering | Folium + Leaflet.js | Interactive browser map |
| Web server | Flask | Lightweight, one endpoint needed |
| Geometry | Shapely + PyProj | Spatial operations + projections |
| Satellite tiles | Esri World Imagery | Free satellite layer |
| Frontend | Vanilla JS | No framework needed for single page |

---

## Performance

| Operation | Time |
|---|---|
| Graph load — first run | ~45 seconds |
| Graph load — cached | ~8 seconds |
| Dijkstra route | < 800 ms |
| A\* route | < 400 ms |
| Full API response | < 1 second |

---

## Scaling Notes

The current implementation runs on a single server with the road graph held in memory. For production scale:

- **Horizontal scaling** — stateless Flask instances behind Nginx load balancer. Each instance holds its own copy of the graph in RAM.
- **Redis cache** — shared route cache across all Flask instances. Same journey is not recalculated twice within 5 minutes.
- **PostgreSQL + PostGIS** — persistent geospatial storage for the road network, with GIST spatial indices for fast nearest-node lookup.
- **Geographic partitioning** — separate server clusters per city. Mumbai cluster loads only the Mumbai graph; Delhi cluster loads Delhi.
- **Kafka** — traffic event stream decouples live incident ingestion from the routing engine.

---

## Future Scope

- Voice turn-by-turn navigation using the Web Speech API
- Multi-modal routing — road + Mumbai local train + metro + walking
- Real GPS probe data ingestion via Kafka
- ML-based ETA prediction using historical congestion patterns
- Multi-city support — Delhi, Bangalore, Pune, Chennai
- Offline maps with locally cached tile packages
- User accounts with saved places and route history
- Native mobile app

---

## Dependencies

```
flask>=3.0.0
osmnx>=2.0.0
networkx>=3.0
folium>=0.14.0
scikit-learn>=1.0
pandas>=1.4
numpy>=1.22
shapely>=2.0
geopandas>=1.0
pyproj>=3.3.0
```

---

## Quick API Test

```bash
curl -X POST http://127.0.0.1:5000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 18.9398, "lon": 72.8354},
    "end":   {"lat": 19.0989, "lon": 72.8267},
    "algorithm": "astar"
  }'
```

---

## Links

- GitHub — <div align="center">


# RouteMaster

### Real-Time Map Navigation System — Mumbai


A Google Maps-style navigation system running **Dijkstra and A\*** on the real Mumbai road network.  
Not a simulation — actual shortest paths on actual streets.

**[Features](#-features) · [Installation](#-installation) · [Usage](#-usage) · [API](#-api-reference) · [Architecture](#-architecture) · [Algorithms](#-algorithm-details)**

---

</div>

## What is RouteMaster?

RouteMaster is a fully working map navigation system built on **real OpenStreetMap road data** for Mumbai. It downloads 3,200+ intersections and 8,500+ road segments, runs graph algorithms on them, and renders the result on an interactive Google Maps-style interface in the browser.

Built for the **System Design (Semester IV)** course — B.Tech CSE 2024–28, ITM Skills University.

---

## Features

- **Real road network** — Mumbai road graph downloaded live from OpenStreetMap via OSMnx
- **Dijkstra's algorithm** — guaranteed shortest path using a min-heap priority queue
- **A\* Search** — faster guided search using the Haversine distance heuristic
- **Compare mode** — run both algorithms at once and see them drawn side by side
- **Traffic simulation** — peak-hour congestion (1.8x–2.8x delay) based on actual time of day
- **Dynamic rerouting** — high-severity incidents trigger alternate route suggestions
- **Google Maps UI** — white sidebar panel, blue route line, start dot, destination pin
- **Satellite toggle** — switch between OpenStreetMap street view and Esri satellite imagery
- **Live traffic feed** — accident alerts, roadwork warnings, signal failures with timestamps
- **REST API** — clean JSON endpoint for route calculation, usable by any frontend

---

## Project Structure

```
routemaster/
├── app.py                 Flask web server + REST API
├── routing_engine.py      Dijkstra · A* · graph loading · ETA calculation
├── traffic_engine.py      Traffic simulation · congestion · rerouting logic
├── map_visualizer.py      Folium map rendering for terminal mode
├── main.py                Standalone terminal navigation interface
├── requirements.txt       Python dependencies
├── README.md              This file
└── templates/
    └── index.html         Google Maps-style single-page web UI
```

---

## Installation

### Requirements

- Python 3.9+
- pip
- Internet connection (for first-time road network download ~10 MB)

### 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/routemaster.git
cd routemaster
```

### 2 — Install dependencies

```bash
pip3 install flask osmnx networkx folium scikit-learn
```

Or using the requirements file:

```bash
pip3 install -r requirements.txt
```

### 3 — Start the server

```bash
python3 app.py
```

### 4 — Open in browser

```
http://127.0.0.1:5000
```

> **Note:** The first run downloads Mumbai's road network from OpenStreetMap — allow 30–60 seconds. Every run after that is instant because OSMnx caches the data locally.

---

## Usage

### Web App

1. Run `python3 app.py`
2. Go to `http://127.0.0.1:5000`
3. Pick a **start location** from the dropdown
4. Pick a **destination**
5. Choose **Dijkstra**, **A\* Search**, or **Compare**
6. Click **Get Directions**

The route draws on real Mumbai streets. The sidebar shows:

- Distance in km
- Free-flow ETA
- Traffic-adjusted ETA with congestion level badge
- Turn-by-turn steps
- Live incident feed

### Terminal Mode

```bash
python3 main.py
```

Select landmarks by number, pick an algorithm, and the route opens as `routemaster_map.html` in your browser.

---

## Available Landmarks

| # | Location | Lat | Lon |
|---|---|---|---|
| 1 | CST Station | 18.9398 | 72.8354 |
| 2 | Bandra Station | 19.0596 | 72.8397 |
| 3 | Juhu Beach | 19.0989 | 72.8267 |
| 4 | Gateway of India | 18.9220 | 72.8347 |
| 5 | Dadar Station | 19.0178 | 72.8478 |
| 6 | Andheri Station | 19.1197 | 72.8464 |
| 7 | Worli Sea Link | 19.0176 | 72.8152 |
| 8 | Haji Ali | 18.9827 | 72.8089 |
| 9 | Marine Drive | 18.9432 | 72.8236 |
| 10 | Powai Lake | 19.1197 | 72.9050 |

---

## API Reference

### `POST /api/route`

Calculate a route between two GPS coordinates.

**Request**

```json
{
  "start":     { "lat": 18.9398, "lon": 72.8354 },
  "end":       { "lat": 19.0989, "lon": 72.8267 },
  "algorithm": "dijkstra"
}
```

`algorithm` accepts: `dijkstra` · `astar` · `both`

**Response**

```json
{
  "status":    "ok",
  "algorithm": "Dijkstra",
  "coords":    [[18.940, 72.835], [18.951, 72.838], "..."],
  "stats": {
    "distance_km": 9.92,
    "eta_min":     19.8
  },
  "traffic": {
    "factor":           1.09,
    "eta_with_traffic": 21.7,
    "level":            "low",
    "updates": [
      { "message": "✅ Road clear",      "time": "14:36:45" },
      { "message": "🚦 Signal failure",  "time": "14:36:45" },
      { "message": "🚧 Road work ahead", "time": "14:36:45" }
    ]
  }
}
```

**Compare response** (when `algorithm: "both"`)

```json
{
  "status":    "ok",
  "algorithm": "both",
  "dijkstra":  { "coords": [...], "stats": { "distance_km": 9.92, "eta_min": 19.8 } },
  "astar":     { "coords": [...], "stats": { "distance_km": 9.92, "eta_min": 19.8 } },
  "traffic":   { "factor": 1.09, "eta_with_traffic": 21.7, "level": "low", "updates": [...] }
}
```

---

### `GET /api/landmarks`

Returns all available landmarks with coordinates.

```bash
curl http://127.0.0.1:5000/api/landmarks
```

```json
{
  "CST Station":      { "lat": 18.9398, "lon": 72.8354 },
  "Bandra Station":   { "lat": 19.0596, "lon": 72.8397 },
  "..."
}
```

---

## Algorithm Details

### Dijkstra's Algorithm

Expands nodes in order of increasing distance from the source using a min-heap. Explores roads in every direction until it reaches the destination. Guarantees the globally optimal shortest path.

```python
path = nx.shortest_path(G, origin_node, dest_node, weight='length')
```

Time complexity: `O((V + E) log V)`

### A\* Search

Adds a heuristic to Dijkstra — the Haversine straight-line distance to the destination. Instead of expanding in all directions, A\* prioritises roads that move closer to the destination. Visits fewer nodes, runs faster, produces the same optimal result.

```python
def heuristic(u, v):
    return haversine(
        G.nodes[u]['y'], G.nodes[u]['x'],
        G.nodes[v]['y'], G.nodes[v]['x']
    )

path = nx.astar_path(G, origin, dest, heuristic=heuristic, weight='length')
```

Time complexity: `O((V + E) log V)` worst case — significantly faster in practice.

### Comparison

| | Dijkstra | A\* |
|---|---|---|
| Result | Optimal | Optimal |
| Speed | Moderate | Faster |
| Heuristic | None | Haversine distance |
| Nodes explored | All reachable | Guided toward goal |
| Best use case | Unknown topology | Geographic routing |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                     CLIENTS                          │
│          Browser · Mobile App · External API         │
└───────────────────────┬──────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼──────────────────────────────┐
│               API GATEWAY + LOAD BALANCER            │
│          Auth · Rate limiting · Request routing      │
└────────┬──────────────┬───────────────┬──────────────┘
         │              │               │
    ┌────▼────┐   ┌──────▼──────┐  ┌───▼────────┐
    │   Map   │   │   Routing   │  │  Traffic   │
    │ Service │   │   Engine    │  │  Service   │
    │  Tiles  │   │ Dijkstra·A* │  │ Congestion │
    └────┬────┘   └──────┬──────┘  └───┬────────┘
         │               │              │
┌────────▼───────────────▼──────────────▼──────────────┐
│                      DATA LAYER                      │
│         PostGIS · Graph Store · Redis · User DB      │
└──────────────────────────────────────────────────────┘
```

### Module responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | HTTP server, request routing, JSON serialisation |
| `routing_engine.py` | Graph loading, Dijkstra, A\*, ETA calculation |
| `traffic_engine.py` | Congestion factors, incident events, rerouting decisions |
| `map_visualizer.py` | Folium map creation, route rendering, marker placement |
| `index.html` | Leaflet map, sidebar UI, fetch API calls, route drawing |

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Road data | OpenStreetMap via OSMnx | Free, real-world, no API key |
| Graph algorithms | NetworkX | Production Dijkstra + A\* built in |
| Map rendering | Folium + Leaflet.js | Interactive browser map |
| Web server | Flask | Lightweight, one endpoint needed |
| Geometry | Shapely + PyProj | Spatial operations + projections |
| Satellite tiles | Esri World Imagery | Free satellite layer |
| Frontend | Vanilla JS | No framework needed for single page |

---

## Performance

| Operation | Time |
|---|---|
| Graph load — first run | ~45 seconds |
| Graph load — cached | ~8 seconds |
| Dijkstra route | < 800 ms |
| A\* route | < 400 ms |
| Full API response | < 1 second |

---

## Scaling Notes

The current implementation runs on a single server with the road graph held in memory. For production scale:

- **Horizontal scaling** — stateless Flask instances behind Nginx load balancer. Each instance holds its own copy of the graph in RAM.
- **Redis cache** — shared route cache across all Flask instances. Same journey is not recalculated twice within 5 minutes.
- **PostgreSQL + PostGIS** — persistent geospatial storage for the road network, with GIST spatial indices for fast nearest-node lookup.
- **Geographic partitioning** — separate server clusters per city. Mumbai cluster loads only the Mumbai graph; Delhi cluster loads Delhi.
- **Kafka** — traffic event stream decouples live incident ingestion from the routing engine.

---

## Future Scope

- Voice turn-by-turn navigation using the Web Speech API
- Multi-modal routing — road + Mumbai local train + metro + walking
- Real GPS probe data ingestion via Kafka
- ML-based ETA prediction using historical congestion patterns
- Multi-city support — Delhi, Bangalore, Pune, Chennai
- Offline maps with locally cached tile packages
- User accounts with saved places and route history
- Native mobile app

---

## Dependencies

```
flask>=3.0.0
osmnx>=2.0.0
networkx>=3.0
folium>=0.14.0
scikit-learn>=1.0
pandas>=1.4
numpy>=1.22
shapely>=2.0
geopandas>=1.0
pyproj>=3.3.0
```

---

## Quick API Test

```bash
curl -X POST http://127.0.0.1:5000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 18.9398, "lon": 72.8354},
    "end":   {"lat": 19.0989, "lon": 72.8267},
    "algorithm": "astar"
  }'
```

---

## Links

- GitHub — https://github.com/avi-0605/RouteMaster
- OpenStreetMap — [openstreetmap.org](https://openstreetmap.org)
- OSMnx docs — [osmnx.readthedocs.io](https://osmnx.readthedocs.io)
- NetworkX docs — [networkx.org](https://networkx.org)
- Leaflet docs — [leafletjs.com](https://leafletjs.com)

---

<div align="center">

Built for ITM Skills University · B.Tech CSE 2024–28 · System Design Semester IV

**RouteMaster — real roads, real algorithms, real results**

</div>
- OpenStreetMap — [openstreetmap.org](https://openstreetmap.org)
- OSMnx docs — [osmnx.readthedocs.io](https://osmnx.readthedocs.io)
- NetworkX docs — [networkx.org](https://networkx.org)
- Leaflet docs — [leafletjs.com](https://leafletjs.com)

---

<div align="center">

Built for ITM Skills University · B.Tech CSE 2024–28 · System Design Semester IV

**RouteMaster — real roads, real algorithms, real results**

</div>

"""
RouteMaster Web App - Flask Backend
Serves the map UI on localhost:5000
"""

from flask import Flask, render_template, jsonify, request
import osmnx as ox
import networkx as nx
import math
import random
import json
import os
from datetime import datetime

app = Flask(__name__)

# Global graph (loaded once)
G = None
G_nodes = None  # for fast lookup

MUMBAI_LANDMARKS = {
    "CST Station":       {"lat": 18.9398, "lon": 72.8354},
    "Bandra Station":    {"lat": 19.0596, "lon": 72.8397},
    "Juhu Beach":        {"lat": 19.0989, "lon": 72.8267},
    "Gateway of India":  {"lat": 18.9220, "lon": 72.8347},
    "Dadar Station":     {"lat": 19.0178, "lon": 72.8478},
    "Andheri Station":   {"lat": 19.1197, "lon": 72.8464},
    "Worli Sea Link":    {"lat": 19.0176, "lon": 72.8152},
    "Haji Ali":          {"lat": 18.9827, "lon": 72.8089},
    "Marine Drive":      {"lat": 18.9432, "lon": 72.8236},
    "Powai Lake":        {"lat": 19.1197, "lon": 72.9050},
}


def load_graph():
    global G
    print("[RouteMaster] Loading Mumbai road network...")
    G = ox.graph_from_point(
        (19.0760, 72.8777),
        dist=6000,
        network_type="drive"
    )
    print(f"[RouteMaster] Loaded {len(G.nodes)} nodes, {len(G.edges)} edges")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_route_coords(path):
    coords = []
    for node in path:
        d = G.nodes[node]
        coords.append([d["y"], d["x"]])
    return coords


def calc_stats(path):
    total = 0
    for u, v in zip(path[:-1], path[1:]):
        ed = G.get_edge_data(u, v)
        if ed:
            total += min(d.get("length", 0) for d in ed.values())
    eta = (total / 1000 / 30) * 60  # 30 km/h avg
    return {"distance_km": round(total/1000, 2), "eta_min": round(eta, 1)}


@app.route("/")
def index():
    return render_template("index.html", landmarks=MUMBAI_LANDMARKS)


@app.route("/api/landmarks")
def get_landmarks():
    return jsonify(MUMBAI_LANDMARKS)


@app.route("/api/route", methods=["POST"])
def get_route():
    data = request.json
    start = data["start"]   # {"lat": x, "lon": y}
    end = data["end"]
    algorithm = data.get("algorithm", "dijkstra")

    try:
        origin = ox.distance.nearest_nodes(G, start["lon"], start["lat"])
        dest = ox.distance.nearest_nodes(G, end["lon"], end["lat"])

        if algorithm == "astar":
            def heuristic(u, v):
                u_d, v_d = G.nodes[u], G.nodes[v]
                return haversine(u_d["y"], u_d["x"], v_d["y"], v_d["x"])
            path = nx.astar_path(G, origin, dest, heuristic=heuristic, weight="length")
            algo_name = "A*"
        elif algorithm == "both":
            path_d = nx.shortest_path(G, origin, dest, weight="length")
            def heuristic(u, v):
                u_d, v_d = G.nodes[u], G.nodes[v]
                return haversine(u_d["y"], u_d["x"], v_d["y"], v_d["x"])
            path_a = nx.astar_path(G, origin, dest, heuristic=heuristic, weight="length")
            stats_d = calc_stats(path_d)
            stats_a = calc_stats(path_a)
            congestion = get_congestion()
            return jsonify({
                "status": "ok",
                "algorithm": "both",
                "dijkstra": {"coords": get_route_coords(path_d), "stats": stats_d},
                "astar": {"coords": get_route_coords(path_a), "stats": stats_a},
                "traffic": {
                    "factor": round(congestion, 2),
                    "eta_with_traffic": round(stats_d["eta_min"] * congestion, 1),
                    "level": traffic_level(congestion),
                    "updates": generate_traffic_updates()
                }
            })
        else:
            path = nx.shortest_path(G, origin, dest, weight="length")
            algo_name = "Dijkstra"

        stats = calc_stats(path)
        congestion = get_congestion()

        return jsonify({
            "status": "ok",
            "algorithm": algo_name,
            "coords": get_route_coords(path),
            "stats": stats,
            "traffic": {
                "factor": round(congestion, 2),
                "eta_with_traffic": round(stats["eta_min"] * congestion, 1),
                "level": traffic_level(congestion),
                "updates": generate_traffic_updates()
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def get_congestion():
    hour = datetime.now().hour
    if 8 <= hour < 11 or 17 <= hour < 21:
        return random.uniform(1.8, 2.8)
    return random.uniform(1.0, 1.4)


def traffic_level(factor):
    if factor < 1.3: return "low"
    if factor < 1.8: return "moderate"
    return "high"


def generate_traffic_updates():
    types = ["🚨 Accident reported", "🚧 Road work ahead", "🚦 Signal failure", "✅ Road clear"]
    updates = []
    for _ in range(3):
        updates.append({
            "message": random.choice(types),
            "time": datetime.now().strftime("%H:%M:%S")
        })
    return updates


if __name__ == "__main__":
    load_graph()
    print("[RouteMaster] Starting web server at http://localhost:5000")
    app.run(debug=False, port=5000)
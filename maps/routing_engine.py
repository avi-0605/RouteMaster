"""
RouteMaster - Routing Engine
Implements Dijkstra and A* algorithms on real Mumbai road network
"""

import osmnx as ox
import networkx as nx
import math
import time
import random


def load_city_graph(city="Mumbai, India", network_type="drive"):
    """Download real road network from OpenStreetMap"""
    print(f"[RouteMaster] Loading road network for {city}...")
    # Use coordinates + distance instead of place name (more reliable)
    G = ox.graph_from_point(
        (19.0760, 72.8777),  # Mumbai city center
        dist=5000,            # 5km radius
        network_type=network_type
    )
    print(f"[RouteMaster] Loaded {len(G.nodes)} nodes and {len(G.edges)} edges")
    return G


def get_nearest_node(G, lat, lon):
    """Find the nearest graph node to given coordinates"""
    return ox.distance.nearest_nodes(G, lon, lat)


def haversine(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance between two coordinates (heuristic for A*)"""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def dijkstra_route(G, origin_node, dest_node, weight="length"):
    """Find shortest path using Dijkstra's algorithm"""
    print("[RouteMaster] Running Dijkstra's algorithm...")
    start = time.time()
    try:
        path = nx.shortest_path(G, origin_node, dest_node, weight=weight)
        duration = time.time() - start
        print(f"[RouteMaster] Dijkstra completed in {duration:.3f}s — {len(path)} nodes in path")
        return path
    except nx.NetworkXNoPath:
        print("[RouteMaster] No path found (Dijkstra)")
        return None


def astar_route(G, origin_node, dest_node):
    """Find shortest path using A* algorithm with haversine heuristic"""
    print("[RouteMaster] Running A* algorithm...")
    start = time.time()

    def heuristic(u, v):
        u_data = G.nodes[u]
        v_data = G.nodes[v]
        return haversine(u_data["y"], u_data["x"], v_data["y"], v_data["x"])

    try:
        path = nx.astar_path(G, origin_node, dest_node, heuristic=heuristic, weight="length")
        duration = time.time() - start
        print(f"[RouteMaster] A* completed in {duration:.3f}s — {len(path)} nodes in path")
        return path
    except nx.NetworkXNoPath:
        print("[RouteMaster] No path found (A*)")
        return None


def calculate_route_stats(G, path):
    """Calculate total distance and estimated travel time"""
    total_length = 0
    for u, v in zip(path[:-1], path[1:]):
        edge_data = G.get_edge_data(u, v)
        # Get minimum length edge (multigraph may have multiple edges)
        if edge_data:
            lengths = [d.get("length", 0) for d in edge_data.values()]
            total_length += min(lengths)

    avg_speed_kmh = 30  # Average urban speed in Mumbai
    time_hours = (total_length / 1000) / avg_speed_kmh
    time_minutes = time_hours * 60

    return {
        "distance_m": round(total_length),
        "distance_km": round(total_length / 1000, 2),
        "eta_minutes": round(time_minutes, 1),
        "nodes": len(path)
    }


def simulate_traffic(G, path, congestion_factor=None):
    """Simulate traffic congestion on route and suggest rerouting"""
    if congestion_factor is None:
        congestion_factor = random.uniform(1.2, 2.5)

    print(f"\n[Traffic] 🚦 Traffic detected! Congestion factor: {congestion_factor:.1f}x")

    stats = calculate_route_stats(G, path)
    new_eta = round(stats["eta_minutes"] * congestion_factor, 1)

    print(f"[Traffic] Original ETA: {stats['eta_minutes']} min → With traffic: {new_eta} min")

    if congestion_factor > 1.8:
        print("[Traffic] ⚠️  Heavy congestion detected. Rerouting recommended.")
        return True, new_eta
    else:
        print("[Traffic] 🟡 Moderate traffic. Continuing on current route.")
        return False, new_eta


# Key Mumbai landmarks with coordinates
MUMBAI_LANDMARKS = {
    "CST Station":          (18.9398, 72.8354),
    "Bandra Station":       (19.0596, 72.8397),
    "Juhu Beach":           (19.0989, 72.8267),
    "Gateway of India":     (18.9220, 72.8347),
    "Dadar Station":        (19.0178, 72.8478),
    "Andheri Station":      (19.1197, 72.8464),
    "Worli Sea Link":       (19.0176, 72.8152),
    "Haji Ali":             (18.9827, 72.8089),
    "Marine Drive":         (18.9432, 72.8236),
    "Powai Lake":           (19.1197, 72.9050),
}
"""
RouteMaster - Main Application
A Google Maps-like navigation system using real Mumbai road data
"""
 
import os
import sys
from routing_engine import (
    load_city_graph, get_nearest_node,
    dijkstra_route, astar_route,
    calculate_route_stats, MUMBAI_LANDMARKS
)
from map_visualizer import (
    create_base_map, add_route_to_map,
    add_markers, add_info_box,
    add_traffic_markers, save_and_open_map
)
from traffic_engine import TrafficEngine
 
 
def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║          🗺️  RouteMaster Navigation System           ║
║         Real-time routing on Mumbai road network     ║
╚══════════════════════════════════════════════════════╝
    """)
 
 
def print_landmarks():
    print("\n📍 Available Mumbai Landmarks:")
    for i, name in enumerate(MUMBAI_LANDMARKS.keys(), 1):
        print(f"  {i:2}. {name}")
 
 
def select_landmark(prompt):
    keys = list(MUMBAI_LANDMARKS.keys())
    while True:
        print_landmarks()
        try:
            choice = int(input(f"\n{prompt} (enter number): ")) - 1
            if 0 <= choice < len(keys):
                name = keys[choice]
                coords = MUMBAI_LANDMARKS[name]
                print(f"  ✅ Selected: {name} ({coords[0]:.4f}, {coords[1]:.4f})")
                return name, coords
            else:
                print("  ❌ Invalid choice, try again.")
        except ValueError:
            print("  ❌ Please enter a valid number.")
 
 
def select_algorithm():
    print("\n🔧 Select Routing Algorithm:")
    print("  1. Dijkstra's Algorithm (guaranteed shortest path)")
    print("  2. A* Algorithm (faster with heuristic)")
    print("  3. Compare Both")
    while True:
        try:
            choice = int(input("Enter choice (1/2/3): "))
            if choice in [1, 2, 3]:
                return choice
        except ValueError:
            pass
        print("  ❌ Enter 1, 2, or 3.")
 
 
def run_navigation(G, start_name, start_coords, end_name, end_coords, algo_choice):
    """Core navigation logic"""
    print(f"\n🔍 Finding route: {start_name} → {end_name}")
 
    origin_node = get_nearest_node(G, start_coords[0], start_coords[1])
    dest_node = get_nearest_node(G, end_coords[0], end_coords[1])
 
    # Run selected algorithm(s)
    path_dijkstra = None
    path_astar = None
 
    if algo_choice in [1, 3]:
        path_dijkstra = dijkstra_route(G, origin_node, dest_node)
    if algo_choice in [2, 3]:
        path_astar = astar_route(G, origin_node, dest_node)
 
    primary_path = path_dijkstra or path_astar
    if not primary_path:
        print("❌ No route found between selected points.")
        return
 
    # Calculate stats
    stats = calculate_route_stats(G, primary_path)
    print(f"\n📊 Route Stats:")
    print(f"   Distance : {stats['distance_km']} km")
    print(f"   ETA      : {stats['eta_minutes']} min (free flow)")
 
    # Traffic analysis
    traffic = TrafficEngine()
    congestion = traffic.get_congestion_factor()
    traffic_eta = traffic.print_traffic_report(stats, congestion)
 
    # Build map
    print("\n🗺️  Building interactive map...")
    m = create_base_map(
        center_lat=(start_coords[0] + end_coords[0]) / 2,
        center_lon=(start_coords[1] + end_coords[1]) / 2,
        zoom=14
    )
 
    algo_label = {1: "Dijkstra", 2: "A*", 3: "Dijkstra + A*"}[algo_choice]
 
    # Draw Dijkstra route in blue
    if path_dijkstra:
        add_route_to_map(m, G, path_dijkstra, color="#4285F4", label="Dijkstra Route")
 
    # Draw A* route in green (slightly offset visually via tooltip)
    if path_astar and algo_choice == 3:
        add_route_to_map(m, G, path_astar, color="#34A853", label="A* Route")
 
    # Add markers
    add_markers(m, start_coords, end_coords, start_name, end_name)
 
    # Add traffic markers
    if len(primary_path) > 10:
        add_traffic_markers(m, G, primary_path)
 
    # Add info panel
    add_info_box(m, stats, start_name, end_name, algo_label, traffic_eta)
 
    # Save and open
    output_dir = os.path.dirname(os.path.abspath(__file__))
    save_and_open_map(m, "routemaster_map.html", output_dir)
 
    # Comparison if both algos run
    if algo_choice == 3 and path_dijkstra and path_astar:
        stats_d = calculate_route_stats(G, path_dijkstra)
        stats_a = calculate_route_stats(G, path_astar)
        print("\n📊 Algorithm Comparison:")
        print(f"  {'':20} {'Dijkstra':>12} {'A*':>12}")
        print(f"  {'Distance (km)':20} {stats_d['distance_km']:>12} {stats_a['distance_km']:>12}")
        print(f"  {'ETA (min)':20} {stats_d['eta_minutes']:>12} {stats_a['eta_minutes']:>12}")
        print(f"  {'Nodes visited':20} {stats_d['nodes']:>12} {stats_a['nodes']:>12}")
 
 
def main():
    print_banner()
 
    # Load graph once (cached by OSMnx after first download)
    print("📡 Connecting to OpenStreetMap...")
    G = load_city_graph("Mumbai, India")
 
    while True:
        print("\n" + "─" * 55)
        print("🚀 Plan a new route (or Ctrl+C to exit)")
 
        start_name, start_coords = select_landmark("Select START location")
        end_name, end_coords = select_landmark("Select DESTINATION")
 
        if start_name == end_name:
            print("⚠️  Start and destination are the same. Pick different locations.")
            continue
 
        algo_choice = select_algorithm()
        run_navigation(G, start_name, start_coords, end_name, end_coords, algo_choice)
 
        again = input("\n\n🔁 Plan another route? (y/n): ").strip().lower()
        if again != "y":
            print("\n👋 Thanks for using RouteMaster!")
            break
 
 
if __name__ == "__main__":
    main()
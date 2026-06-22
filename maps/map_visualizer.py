"""
RouteMaster - Map Visualizer
Renders interactive maps with routes using Folium + OpenStreetMap
"""

import folium
import webbrowser
import os


def create_base_map(center_lat=19.0760, center_lon=72.8777, zoom=13):
    """Create a base folium map centered on Mumbai"""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",
        attr="© OpenStreetMap contributors"
    )
    return m


def add_route_to_map(m, G, path, color="blue", label="Route"):
    """Draw route path on the map"""
    route_coords = []
    for node in path:
        node_data = G.nodes[node]
        route_coords.append((node_data["y"], node_data["x"]))

    folium.PolyLine(
        route_coords,
        color=color,
        weight=6,
        opacity=0.85,
        tooltip=label
    ).add_to(m)

    return route_coords


def add_markers(m, start_coords, end_coords, start_name="Start", end_name="Destination"):
    """Add start and end markers to map"""
    # Start marker (green)
    folium.Marker(
        location=start_coords,
        popup=folium.Popup(f"<b>🟢 Start</b><br>{start_name}", max_width=200),
        tooltip=f"Start: {start_name}",
        icon=folium.Icon(color="green", icon="play", prefix="fa")
    ).add_to(m)

    # End marker (red)
    folium.Marker(
        location=end_coords,
        popup=folium.Popup(f"<b>🔴 Destination</b><br>{end_name}", max_width=200),
        tooltip=f"Destination: {end_name}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa")
    ).add_to(m)


def add_info_box(m, stats, start_name, end_name, algorithm="Dijkstra", traffic_eta=None):
    """Add route information panel to map"""
    traffic_html = ""
    if traffic_eta:
        traffic_html = f"""
        <tr><td><b>🚦 Traffic ETA</b></td><td style="color:red">{traffic_eta} min</td></tr>
        """

    html = f"""
    <div style="
        position: fixed;
        top: 10px; right: 10px;
        width: 280px;
        background: white;
        border: 2px solid #4285F4;
        border-radius: 10px;
        padding: 15px;
        font-family: Arial, sans-serif;
        font-size: 13px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    ">
        <div style="font-size:16px; font-weight:bold; color:#4285F4; margin-bottom:10px;">
            🗺️ RouteMaster
        </div>
        <table style="width:100%; border-collapse:collapse;">
            <tr><td><b>📍 From</b></td><td>{start_name}</td></tr>
            <tr><td><b>🏁 To</b></td><td>{end_name}</td></tr>
            <tr><td><b>📏 Distance</b></td><td>{stats['distance_km']} km</td></tr>
            <tr><td><b>⏱️ ETA</b></td><td>{stats['eta_minutes']} min</td></tr>
            <tr><td><b>🔧 Algorithm</b></td><td>{algorithm}</td></tr>
            {traffic_html}
        </table>
        <div style="margin-top:10px; font-size:11px; color:#888;">
            Powered by OpenStreetMap + OSMnx
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(html))


def add_traffic_markers(m, G, path):
    """Add simulated traffic congestion markers along the route"""
    import random
    # Pick 2-3 random spots on the route to show traffic
    traffic_points = random.sample(path[5:-5], min(3, len(path) - 10))
    for node in traffic_points:
        node_data = G.nodes[node]
        folium.CircleMarker(
            location=(node_data["y"], node_data["x"]),
            radius=10,
            color="orange",
            fill=True,
            fill_color="orange",
            fill_opacity=0.7,
            tooltip="🚦 Traffic congestion detected"
        ).add_to(m)


def save_and_open_map(m, filename="routemaster_map.html", output_dir="."):
    """Save map to HTML and open in browser"""
    filepath = os.path.join(output_dir, filename)
    m.save(filepath)
    abs_path = os.path.abspath(filepath)
    print(f"\n[RouteMaster] 🗺️  Map saved → {abs_path}")
    print("[RouteMaster] Opening in browser...")
    webbrowser.open(f"file://{abs_path}")
    return abs_path
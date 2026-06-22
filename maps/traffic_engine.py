"""
RouteMaster - Traffic Analysis Module
Simulates real-time traffic updates and dynamic rerouting
"""

import random
import time
from datetime import datetime


class TrafficEngine:
    """Simulates a real-time traffic analysis system"""

    PEAK_HOURS = [(8, 11), (17, 21)]  # Morning and evening rush hours

    def __init__(self):
        self.traffic_updates = []
        self.incident_zones = []

    def get_congestion_factor(self):
        """Return congestion multiplier based on time of day"""
        hour = datetime.now().hour
        for start, end in self.PEAK_HOURS:
            if start <= hour < end:
                factor = random.uniform(1.8, 3.0)
                print(f"[Traffic] 🔴 Peak hour traffic! Factor: {factor:.1f}x")
                return factor
        factor = random.uniform(1.0, 1.5)
        print(f"[Traffic] 🟢 Normal traffic. Factor: {factor:.1f}x")
        return factor

    def simulate_live_update(self, path_length):
        """Simulate receiving a live traffic update"""
        update = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": random.choice(["accident", "roadwork", "signal_failure", "clear"]),
            "severity": random.choice(["low", "medium", "high"]),
            "affected_segment": random.randint(0, path_length - 1)
        }
        self.traffic_updates.append(update)

        icon = {"accident": "🚨", "roadwork": "🚧", "signal_failure": "🚦", "clear": "✅"}
        print(f"[Traffic Live] {icon[update['type']]} [{update['timestamp']}] "
              f"{update['type'].upper()} — severity: {update['severity']}")
        return update

    def should_reroute(self, update):
        """Decide if rerouting is needed based on traffic update"""
        if update["type"] == "clear":
            return False
        if update["severity"] == "high":
            print("[Traffic] ⚠️  High severity incident. Triggering reroute...")
            return True
        if update["severity"] == "medium" and update["type"] == "accident":
            print("[Traffic] ⚠️  Accident detected. Rerouting to avoid delay...")
            return True
        return False

    def get_eta_with_traffic(self, base_eta_minutes, congestion_factor):
        """Calculate realistic ETA accounting for traffic"""
        traffic_eta = base_eta_minutes * congestion_factor
        # Add random variance (±10%)
        variance = traffic_eta * random.uniform(-0.1, 0.1)
        return round(traffic_eta + variance, 1)

    def print_traffic_report(self, base_stats, congestion_factor):
        """Print a full traffic analysis report"""
        print("\n" + "=" * 50)
        print("        📊 TRAFFIC ANALYSIS REPORT")
        print("=" * 50)
        print(f"  Base Distance    : {base_stats['distance_km']} km")
        print(f"  Free-flow ETA    : {base_stats['eta_minutes']} min")
        print(f"  Congestion Level : {congestion_factor:.1f}x")

        eta = self.get_eta_with_traffic(base_stats['eta_minutes'], congestion_factor)
        if congestion_factor < 1.3:
            level = "🟢 LOW"
        elif congestion_factor < 1.8:
            level = "🟡 MODERATE"
        else:
            level = "🔴 HIGH"

        print(f"  Traffic Status   : {level}")
        print(f"  Estimated ETA    : {eta} min")
        print("=" * 50)

        # Simulate 3 live updates
        print("\n[Traffic] Receiving live updates...")
        for _ in range(3):
            time.sleep(0.3)
            self.simulate_live_update(100)

        return eta
import time
import random
import math


class GPSTracker:
    """
    Self GPS module for the Homestead Guardian.

    Tracks the robot's own position (latitude, longitude, altitude) and
    maintains a movement history.  In a real deployment this would read
    from a GNSS hardware driver (e.g. via ROS NavSatFix messages).
    """

    EARTH_RADIUS_M = 6_371_000.0  # metres

    def __init__(self, initial_lat: float = 0.0, initial_lon: float = 0.0,
                 initial_alt: float = 0.0):
        self.lat = initial_lat
        self.lon = initial_lon
        self.alt = initial_alt
        self.history: list[dict] = []
        self._record()

    # ------------------------------------------------------------------
    # Core position interface
    # ------------------------------------------------------------------

    def update_position(self, lat: float, lon: float, alt: float = 0.0) -> None:
        """Update the robot's current GPS position."""
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self._record()

    def get_position(self) -> dict:
        """Return the current position as a dict."""
        return {"lat": self.lat, "lon": self.lon, "alt": self.alt,
                "timestamp": time.time()}

    def distance_to(self, lat: float, lon: float) -> float:
        """
        Returns the great-circle distance in metres between the robot's
        current position and the given coordinates (Haversine formula).
        """
        lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * self.EARTH_RADIUS_M * math.asin(math.sqrt(a))

    def bearing_to(self, lat: float, lon: float) -> float:
        """
        Returns the initial bearing in degrees (0–360) from the robot's
        current position to the target coordinates.
        """
        lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    # ------------------------------------------------------------------
    # History helpers
    # ------------------------------------------------------------------

    def _record(self) -> None:
        self.history.append({"lat": self.lat, "lon": self.lon,
                              "alt": self.alt, "timestamp": time.time()})

    def path_length(self) -> float:
        """Total distance (metres) travelled across all recorded positions."""
        total = 0.0
        for i in range(1, len(self.history)):
            prev = self.history[i - 1]
            curr = self.history[i]
            total += self._haversine(prev["lat"], prev["lon"],
                                     curr["lat"], curr["lon"])
        return total

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        R = GPSTracker.EARTH_RADIUS_M
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a))

    # ------------------------------------------------------------------
    # Demo / simulation
    # ------------------------------------------------------------------

    def simulate_patrol(self, steps: int = 5, step_size_deg: float = 0.0001) -> None:
        """Simulates random patrol movement and prints position updates."""
        print("=== GPS Self-Tracking Simulation ===")
        for i in range(steps):
            dlat = random.uniform(-step_size_deg, step_size_deg)
            dlon = random.uniform(-step_size_deg, step_size_deg)
            self.update_position(self.lat + dlat, self.lon + dlon)
            pos = self.get_position()
            print(f"  Step {i + 1}: lat={pos['lat']:.6f}  lon={pos['lon']:.6f}  "
                  f"alt={pos['alt']:.1f}m")
        print(f"  Total path length: {self.path_length():.2f} m")


if __name__ == "__main__":
    tracker = GPSTracker(initial_lat=37.7749, initial_lon=-122.4194)
    tracker.simulate_patrol()

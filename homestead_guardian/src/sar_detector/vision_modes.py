import random


class HeatSensorVision:
    """
    Simulates a thermal / heat-sensor vision mode for the Homestead Guardian.

    Processes a frame (represented as a dict of pixel regions with temperature
    readings) and returns a list of detected heat signatures above a configurable
    threshold.
    """

    def __init__(self, threshold_celsius: float = 36.0):
        # Minimum temperature (°C) to flag a region as a heat signature
        self.threshold_celsius = threshold_celsius
        self.mode = "heat_sensor"

    def process_frame(self, frame: dict) -> list:
        """
        Accepts a frame dict mapping region labels to temperature values (°C).
        Returns a list of detections for regions that exceed the threshold.

        Example frame::

            {
                "region_A": 22.5,
                "region_B": 37.1,
                "region_C": 40.3,
            }
        """
        detections = []
        for region, temp in frame.items():
            if temp >= self.threshold_celsius:
                detections.append(
                    {
                        "region": region,
                        "temperature_c": temp,
                        "label": "heat_signature",
                    }
                )
        return detections

    def simulate_scan(self, num_regions: int = 6) -> list:
        """Generates a random thermal frame and returns detections."""
        frame = {
            f"region_{chr(65 + i)}": round(random.uniform(18.0, 42.0), 1)
            for i in range(num_regions)
        }
        print(f"\n[{self.mode.upper()}] Thermal scan:")
        for region, temp in frame.items():
            flag = " <-- DETECTED" if temp >= self.threshold_celsius else ""
            print(f"  {region}: {temp}°C{flag}")
        detections = self.process_frame(frame)
        print(f"  Total heat signatures: {len(detections)}")
        return detections


class NightVision:
    """
    Simulates a night-vision mode for the Homestead Guardian.

    Applies simulated low-light amplification to a frame (represented as a
    dict of pixel regions with luminance values 0.0–1.0) and classifies each
    region as visible or obscured after amplification.
    """

    def __init__(self, amplification_gain: float = 8.0, visibility_threshold: float = 0.1):
        # Multiplicative gain applied to raw luminance values
        self.amplification_gain = amplification_gain
        # Minimum amplified luminance required to classify a region as visible
        self.visibility_threshold = visibility_threshold
        self.mode = "night_vision"

    def amplify(self, luminance: float) -> float:
        """Applies gain and clamps the result to [0.0, 1.0]."""
        return min(1.0, luminance * self.amplification_gain)

    def process_frame(self, frame: dict) -> list:
        """
        Accepts a frame dict mapping region labels to raw luminance values
        (0.0 = pitch black, 1.0 = fully lit).
        Returns a list of region results after amplification.

        Example frame::

            {
                "region_A": 0.02,
                "region_B": 0.15,
                "region_C": 0.005,
            }
        """
        results = []
        for region, raw_lum in frame.items():
            amplified = self.amplify(raw_lum)
            results.append(
                {
                    "region": region,
                    "raw_luminance": raw_lum,
                    "amplified_luminance": round(amplified, 3),
                    "visible": amplified >= self.visibility_threshold,
                }
            )
        return results

    def simulate_scan(self, num_regions: int = 6) -> list:
        """Generates a random low-light frame and returns amplified results."""
        frame = {
            f"region_{chr(65 + i)}": round(random.uniform(0.0, 0.2), 3)
            for i in range(num_regions)
        }
        print(f"\n[{self.mode.upper()}] Low-light scan (gain x{self.amplification_gain}):")
        results = self.process_frame(frame)
        for r in results:
            status = "VISIBLE" if r["visible"] else "obscured"
            print(
                f"  {r['region']}: raw={r['raw_luminance']:.3f}  "
                f"amplified={r['amplified_luminance']:.3f}  [{status}]"
            )
        visible_count = sum(1 for r in results if r["visible"])
        print(f"  Visible regions: {visible_count}/{len(results)}")
        return results


if __name__ == "__main__":
    print("=== Homestead Guardian Vision Modes Demo ===")

    heat_cam = HeatSensorVision(threshold_celsius=36.0)
    heat_cam.simulate_scan()

    night_cam = NightVision(amplification_gain=8.0, visibility_threshold=0.1)
    night_cam.simulate_scan()

"""Test the improved fallback layout for a large plot."""
from app.fallback_plans import build_fallback_plan, get_fallback_key
import math

# Test: 1BHK 2bath on massive 25x20m plot (500m2)
key = get_fallback_key(1, 2, 1, 1, 1)
W, H = 25, 20
rooms = build_fallback_plan(key, W, H) # plot length, plot width

print(f"=== FALLBACK PLAN ({W}x{H}m, 1BHK, 500m²) ===")
for r in rooms:
    w = r["p2"]["x"] - r["p1"]["x"]
    h = r["p2"]["y"] - r["p1"]["y"]
    t = r["metadata"]["type"]
    label = r["label"]
    area = w * h
    print(f"{label:20s} {t:10s} {w:.1f}x{h:.1f}m = {area:.1f}m²")

# Check basic logic
living = next((r for r in rooms if r["metadata"]["type"] == "living"), None)
if living:
    w = living["p2"]["x"] - living["p1"]["x"]
    h = living["p2"]["y"] - living["p1"]["y"]
    assert w * h < 90, f"FAIL: Living room too huge ({w*h:.1f}m²)"
    print(f"✓ Living room size reasonable ({w*h:.1f}m²)")

for r in rooms:
    t = r["metadata"]["type"]
    w = r["p2"]["x"] - r["p1"]["x"]
    h = r["p2"]["y"] - r["p1"]["y"]
    area = w * h
    
    if "study" in t:
        assert area < 60, f"FAIL: Study too huge ({area:.1f}m²)"
        print(f"✓ Study size reasonable ({area:.1f}m²)")
    if "store" in t and area > 30:
        print(f"WARNING: Large Store Room ({area:.1f}m²)")
    if "hallway" in t and area > 100:
        print(f"WARNING: Huge Hallway/Foyer ({area:.1f}m²)")


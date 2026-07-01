"""Test fallback layout with 2BHK on large plot (50x40m)"""
from app.fallback_plans import build_fallback_plan, get_fallback_key

key = get_fallback_key(2, 2, 1, 1, 1)
rooms = build_fallback_plan(key, 50, 40)

print("=" * 65)
print(f"2BHK on 50x40m plot (2000m2) - Rooms generated: {len(rooms)}")
print("=" * 65)

total_area = 0
for r in rooms:
    w = r["p2"]["x"] - r["p1"]["x"]
    h = r["p2"]["y"] - r["p1"]["y"]
    area = w * h
    total_area += area
    t = r["metadata"]["type"]
    print(f"  {r['label']:20s} {t:10s} {w:5.1f} x {h:5.1f}m = {area:7.1f} m2")

print("-" * 65)
print(f"  Total area: {total_area:.1f} m2 (plot: 2000.0 m2)")

# Check for unwanted rooms
unwanted = ["Home Office", "Gym", "Walk-in Closet", "Store", "Utility", "Foyer", "Dining", "Study"]
found_unwanted = [r["label"] for r in rooms if any(u.lower() in r["label"].lower() for u in unwanted)]
if found_unwanted:
    print(f"\n  WARNING: Unwanted rooms found: {found_unwanted}")
else:
    print(f"\n  OK: No unwanted filler rooms!")

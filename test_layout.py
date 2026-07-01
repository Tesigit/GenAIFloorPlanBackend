"""Quick test - minimal output"""
from app.fallback_plans import build_fallback_plan, get_fallback_key

key = get_fallback_key(2, 1, 1, 1, 1)
rooms = build_fallback_plan(key, 23, 33)
for r in rooms:
    w = r["p2"]["x"] - r["p1"]["x"]
    h = r["p2"]["y"] - r["p1"]["y"]
    t = r["metadata"]["type"]
    print(f"{r['label']:18s} {t:10s} {w:.1f}x{h:.1f}m = {w*h:.1f}m2")

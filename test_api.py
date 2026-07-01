"""Test the full API endpoint locally."""
import urllib.request, json

payload = {
    "length": 33, "width": 23,
    "bedrooms": 2, "bathrooms": 1, "kitchens": 1,
    "livingRooms": 1, "balconies": 1,
    "stylePreference": "Modern", "prompt": "east facing",
    "specialRequirements": []
}

req = urllib.request.Request(
    "http://localhost:8000/api/generate",
    json.dumps(payload).encode(),
    {"Content-Type": "application/json"}
)

try:
    resp = urllib.request.urlopen(req, timeout=90)
    data = json.loads(resp.read())
    print("STATUS: OK")
    print(f"Rooms: {len(data['plan']['rooms'])}")
    for r in data["plan"]["rooms"]:
        w = r["p2"]["x"] - r["p1"]["x"]
        h = r["p2"]["y"] - r["p1"]["y"]
        t = r.get("metadata", {}).get("type", "?")
        print(f"  {r['label']:20s} {t:10s} {w:.1f}x{h:.1f}m = {w*h:.1f}m2")
        if "bathroom" in r["label"].lower():
            assert w <= 3.5, f"FAIL: Bathroom too wide: {w}m"
            assert h <= 3.5, f"FAIL: Bathroom too tall: {h}m"
            print(f"    ✓ Bathroom size OK")
    print("\nAll checks passed!")
except Exception as e:
    print(f"ERROR: {e}")

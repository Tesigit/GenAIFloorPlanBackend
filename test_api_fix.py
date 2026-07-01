"""Test the /generate API endpoint with 2BHK on 50x40m plot."""
import urllib.request, json

url = "http://localhost:8000/generate"
body = {
    "length": 50,
    "width": 40,
    "bedrooms": 2,
    "bathrooms": 2,
    "kitchens": 1,
    "livingRooms": 1,
    "balconies": 1,
    "stylePreference": "minimalist",
    "units": "meters",
}
data = json.dumps(body).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    rooms = result["plan"]["rooms"]
    print(f"{'='*65}")
    print(f"API /generate - 2BHK on 50x40m - Rooms: {len(rooms)} | Valid: {result['valid']}")
    print(f"{'='*65}")
    for r in rooms:
        w = r["p2"]["x"] - r["p1"]["x"]
        h = r["p2"]["y"] - r["p1"]["y"]
        area = w * h
        rtype = r.get("metadata", {}).get("type", "??")
        print(f"  {r['label']:22s} {rtype:10s} {w:5.1f} x {h:5.1f}m = {area:7.1f} m2")

    print(f"\nMessages:")
    for m in result.get("messages", []):
        print(f"  > {m}")

    # Check for unwanted rooms
    unwanted_keywords = ["Home Office", "Gym", "Walk-in Closet", "Store", "Utility", "Foyer", "Dining", "Study", "Dressing", "Library", "Guest"]
    found = [r["label"] for r in rooms if any(u.lower() in r["label"].lower() for u in unwanted_keywords)]
    if found:
        print(f"\n  WARNING: Unwanted rooms: {found}")
    else:
        print(f"\n  OK: No unwanted filler rooms!")
except Exception as e:
    print(f"Error: {e}")

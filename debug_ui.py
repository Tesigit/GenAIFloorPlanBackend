import urllib.request, json
payload = {
    "length": 12, "width": 8, "bedrooms": 3, "bathrooms": 2, 
    "kitchens": 1, "livingRooms": 1, "balconies": 1,
    "prompt": "pooja room in the living area",
    "stylePreference": "modern",
    "specialRequirements": []
}
req = urllib.request.Request(
    "http://localhost:8000/generate",
    json.dumps(payload).encode(),
    {"Content-Type": "application/json"}
)
try:
    resp = urllib.request.urlopen(req, timeout=90)
    data = json.loads(resp.read())
    with open("debug_ui.txt", "w", encoding="utf-8") as f:
        f.write(f"Source: {data['source']}\n")
        f.write(f"Valid: {data['valid']}\n")
        f.write(f"Messages: {data['messages']}\n")
        for r in data["plan"]["rooms"]:
            w = r['p2']['x'] - r['p1']['x']
            h = r['p2']['y'] - r['p1']['y']
            f.write(f"  {r['label']:15s} | {r['p1']['x']:4.1f},{r['p1']['y']:4.1f} to {r['p2']['x']:4.1f},{r['p2']['y']:4.1f} ({w}x{h})\n")
except Exception as e:
    with open("debug_ui.txt", "w") as f:
        f.write(f"Error: {e}")

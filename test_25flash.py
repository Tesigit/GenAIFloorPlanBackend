"""Test gemini-2.5-flash with a real floor plan request."""
import urllib.request, json, ssl, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY", "")
print(f"Key: {key[:12]}...")

prompt = """Generate a 2BHK floor plan for a 12x8m plot.
Include: 2 bedrooms, 2 bathrooms (attached), 1 kitchen, 1 living room, 1 balcony.
Living room at front, bedrooms at back. Kitchen adjacent to living. Each bathroom next to its bedroom.
Output ONLY valid JSON in format:
{"rooms":[{"label":"Living Room","p1":{"x":0,"y":0},"p2":{"x":5,"y":4},"metadata":{"type":"living"}}]}"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
body = json.dumps({
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.5}
}).encode("utf-8")

req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
ctx = ssl._create_unverified_context()

print("Sending to gemini-2.5-flash...")
try:
    with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
        data = json.loads(r.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        rooms = parsed.get("rooms", [])
        print(f"\n✅ SUCCESS! Got {len(rooms)} rooms:")
        for room in rooms:
            print(f"  - {room['label']}: ({room['p1']['x']},{room['p1']['y']}) → ({room['p2']['x']},{room['p2']['y']})")
except urllib.error.HTTPError as e:
    b = e.read().decode()[:300]
    print(f"❌ HTTP {e.code}: {b}")
except Exception as e:
    print(f"❌ Error: {e}")

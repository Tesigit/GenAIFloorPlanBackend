"""Test Groq API for floor plan generation."""
import urllib.request, json, ssl, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GROQ_API_KEY", "")
print(f"Key: {key[:12]}...")

SYSTEM = """You are a residential architect. Output ONLY valid JSON. No markdown, no explanation.
RULES: All rooms tile EXACTLY to fill the plot rectangle. p1=top-left, p2=bottom-right. Living Room at front (y near 0). Bedrooms at back. Each Bathroom attached to a Bedroom.
FORMAT: {"rooms":[{"label":"Living Room","p1":{"x":0,"y":0},"p2":{"x":8,"y":3},"metadata":{"type":"living"}}]}"""

USER = """Generate a 2BHK floor plan for a 10x8m plot.
Rooms: Living Room, Kitchen, Master Bedroom (attached Bathroom 1), Bedroom 2 (attached Bathroom 2).
All rooms fill 10x8m. Living Room at front. Bedrooms at back. Output ONLY JSON."""

url = "https://api.groq.com/openai/v1/chat/completions"
body = json.dumps({
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER}
    ],
    "temperature": 0.4,
    "max_tokens": 2048
}).encode("utf-8")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}",
    "User-Agent": "curl/7.68.0"
}
ctx = ssl._create_unverified_context()
req = urllib.request.Request(url, data=body, headers=headers)

print("Calling Groq llama-3.3-70b-versatile...")
try:
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        d = json.loads(r.read())
        text = d["choices"][0]["message"]["content"]
        # Extract JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        parsed = json.loads(text[start:end])
        rooms = parsed.get("rooms", [])
        print(f"\n✅ SUCCESS! {len(rooms)} rooms:")
        for room in rooms:
            w = abs(room['p2']['x'] - room['p1']['x'])
            h = abs(room['p2']['y'] - room['p1']['y'])
            print(f"  {room['label']}: {w:.1f}x{h:.1f}m at ({room['p1']['x']},{room['p1']['y']})")
        print(f"\nTime to show this in the app!")
except urllib.error.HTTPError as e:
    b = e.read().decode()[:300]
    print(f"❌ HTTP {e.code}: {b}")
except Exception as e:
    print(f"❌ Error: {e}")

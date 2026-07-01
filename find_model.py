"""Find working model and test actual floor plan generation."""
import urllib.request, json, ssl, os, sys
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY", "")
print(f"Key: {key[:12]}...")
ctx = ssl._create_unverified_context()

# Get all models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
try:
    with urllib.request.urlopen(url, timeout=10, context=ctx) as r:
        d = json.loads(r.read())
        gen_models = [m["name"] for m in d.get("models", [])
                      if "generateContent" in str(m.get("supportedGenerationMethods", []))]
        print(f"Found {len(gen_models)} models: {gen_models[:5]}")
except Exception as e:
    print(f"Model list failed: {e}")
    gen_models = ["models/gemini-2.0-flash", "models/gemini-2.0-flash-lite", "models/gemini-1.5-flash", "models/gemini-2.5-flash"]

# Short floor plan prompt
prompt = 'Generate a simple 2BHK floor plan JSON for a 12x8m plot. 2 bedrooms with attached bathrooms, kitchen, living room. Output ONLY JSON: {"rooms":[{"label":"Living Room","p1":{"x":0,"y":0},"p2":{"x":8,"y":3},"metadata":{"type":"living"}}]}'

print("\nTesting models for generation...")
for model in gen_models:
    murl = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={key}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}
    }).encode("utf-8")
    req = urllib.request.Request(murl, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            d = json.loads(r.read().decode("utf-8"))
            text = d["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            rooms = parsed.get("rooms", [])
            print(f"\n✅ WORKS: {model}")
            print(f"   Rooms: {[r['label'] for r in rooms]}")
            print(f"\nUSE THIS MODEL: {model}")
            sys.exit(0)
    except urllib.error.HTTPError as e:
        b = e.read().decode()[:80]
        print(f"  ✗ {e.code} {model}")
    except Exception as e:
        print(f"  ✗ ERR {model}: {str(e)[:80]}")

print("\n❌ No model worked")

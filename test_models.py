"""Find and test which Gemini model works right now."""
import urllib.request, json, ssl, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY", "")
print(f"Key: {key[:12]}...")
ctx = ssl._create_unverified_context()

# Get all available models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
with urllib.request.urlopen(url, timeout=10, context=ctx) as r:
    d = json.loads(r.read())
    models = [m["name"] for m in d.get("models", [])
              if "generateContent" in str(m.get("supportedGenerationMethods", []))]

print(f"\nAll {len(models)} generative models:")
for m in models:
    print(f"  {m}")

print("\n--- Testing each for generation ---")
for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={key}"
    body = json.dumps({
        "contents": [{"parts": [{"text": "Output only: {\"ok\":true}"}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            print(f"  WORKS: {model}")
            break
    except urllib.error.HTTPError as e:
        b = e.read().decode()[:80]
        print(f"  FAIL {e.code}: {model}")
    except Exception as e:
        print(f"  ERR: {model} - {e}")

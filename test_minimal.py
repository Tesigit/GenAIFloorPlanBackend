"""Minimal test: single API call with gemini-2.0-flash-lite."""
import urllib.request, json, ssl, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY", "")
print(f"Key: {key[:12]}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={key}"
body = json.dumps({
    "contents": [{"parts": [{"text": "Generate a simple JSON object with a greeting field. Output only valid JSON."}]}],
    "generationConfig": {"responseMimeType": "application/json"}
}).encode("utf-8")

req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
ctx = ssl._create_unverified_context()

try:
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"SUCCESS: {text[:500]}")
except urllib.error.HTTPError as e:
    body_text = e.read().decode("utf-8", errors="replace")
    print(f"HTTP {e.code}")
    print(f"Error: {body_text[:500]}")
except Exception as e:
    print(f"Error: {e}")

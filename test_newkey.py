"""Find and test working models on newkey."""
import urllib.request, json, ssl, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY", "")
print(f"Key: {key[:12]}...")
ctx = ssl._create_unverified_context()

# Try both v1 and v1beta
for base in ["https://generativelanguage.googleapis.com/v1", 
             "https://generativelanguage.googleapis.com/v1beta"]:
    url = f"{base}/models?key={key}"
    try:
        with urllib.request.urlopen(url, timeout=10, context=ctx) as r:
            d = json.loads(r.read())
            models = [m["name"] for m in d.get("models", [])
                      if "generateContent" in str(m.get("supportedGenerationMethods", []))]
            print(f"\n{base}: {len(models)} models")
            for m in models[:15]:
                print(f"  {m}")
            break
    except Exception as e:
        print(f"{base}: {e}")

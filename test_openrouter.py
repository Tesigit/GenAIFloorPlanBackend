"""Test OpenRouter API — check errors and find working model."""
import urllib.request, json, ssl, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("OPENROUTER_API_KEY", "")
print(f"Key: {key[:18]}...")
ctx = ssl._create_unverified_context()
url = "https://openrouter.ai/api/v1/chat/completions"

def test_model(model_id, text="Say hi as JSON: {\"hello\":true}"):
    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": text}],
        "max_tokens": 200
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "HTTP-Referer": "http://localhost:5173",
    }
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            d = json.loads(r.read())
            return "OK", d["choices"][0]["message"]["content"][:100]
    except urllib.error.HTTPError as e:
        b = e.read().decode()[:300]
        return f"HTTP {e.code}", b
    except Exception as e:
        return "ERR", str(e)[:100]

models_to_test = [
    "deepseek/deepseek-chat",          # Paid but very cheap
    "deepseek/deepseek-chat-v3-0324",  # Paid 
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-14b:free",
]

for m in models_to_test:
    status, msg = test_model(m)
    print(f"\n{m}")
    print(f"  Status: {status}")
    print(f"  Reply:  {msg[:120]}")

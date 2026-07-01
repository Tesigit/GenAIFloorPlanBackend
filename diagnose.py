"""Full diagnostic for GPLAN pipeline."""
import os, sys, json, urllib.request, urllib.error

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("GPLAN FULL DIAGNOSTIC")
print("=" * 60)

# 1. ENV FILE
print("\n[1] .env file")
env_path = os.path.join(os.getcwd(), ".env")
if os.path.isfile(env_path):
    print(f"  OK Found: {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key_name = line.split("=")[0]
                val = line.split("=", 1)[1] if "=" in line else ""
                if "<" in val:
                    print(f"  WARN {key_name} = {val[:50]}... (HAS PLACEHOLDER!)")
                else:
                    print(f"  OK {key_name} = {val[:15]}...")
else:
    print(f"  FAIL NOT FOUND at {env_path}")

# 2. LOAD ENV
try:
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print("\n[2] dotenv loaded: OK")
except Exception as e:
    print(f"\n[2] dotenv: FAIL {e}")

# 3. API KEY
print("\n[3] API Key")
gemini_key = os.getenv("GEMINI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")
api_key = gemini_key or google_key
if api_key:
    print(f"  OK Key found: {api_key[:12]}...")
    print(f"  Key length: {len(api_key)}")
else:
    print("  FAIL NO API KEY FOUND")

# 4. MONGODB
print("\n[4] MongoDB URI")
mongo_uri = os.getenv("MONGODB_URI")
if mongo_uri:
    if "<" in mongo_uri:
        print(f"  WARN URI has placeholder: {mongo_uri[:60]}...")
        print("  --> You MUST replace <db_password> with your actual MongoDB password")
    else:
        print(f"  OK URI looks valid: {mongo_uri[:40]}...")
else:
    print("  WARN Not set (will skip DB examples, but generation can work)")

# 5. LIST AVAILABLE MODELS
print("\n[5] Available Gemini Flash models")
if api_key:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            flash_models = [
                m["name"] for m in data.get("models", [])
                if "flash" in m["name"].lower()
                and "generateContent" in str(m.get("supportedGenerationMethods", []))
            ]
            for m in flash_models:
                print(f"  - {m}")
            if not flash_models:
                print("  FAIL No flash models found!")
    except Exception as e:
        print(f"  FAIL Failed to list models: {e}")

# 6. TEST GENERATION
print("\n[6] Test Gemini generation")
if api_key:
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-2.5-flash-preview-05-20",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
    ]
    working_model = None
    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            body = {"contents": [{"parts": [{"text": "Reply with exactly one word: WORKING"}]}]}
            data = json.dumps(body).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"  OK {model_name}: {text.strip()[:50]}")
                working_model = model_name
                break
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")[:200]
            print(f"  FAIL {model_name}: HTTP {e.code} -- {body_text[:100]}")
        except Exception as e:
            print(f"  FAIL {model_name}: {type(e).__name__}: {str(e)[:100]}")

    if working_model:
        print(f"\n  >>> WORKING MODEL: {working_model}")
    else:
        print("\n  >>> ALL MODELS FAILED - Check API key quota at https://aistudio.google.com/")

# 7. BACKEND HEALTH
print("\n[7] Backend server health")
try:
    with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as r:
        print(f"  OK Backend running: {r.read().decode()}")
except Exception as e:
    print(f"  FAIL Backend not reachable: {e}")

# 8. FRONTEND
print("\n[8] Frontend proxy")
try:
    with urllib.request.urlopen("http://localhost:5173", timeout=5) as r:
        print(f"  OK Frontend running (HTTP {r.getcode()})")
except Exception as e:
    print(f"  FAIL Frontend not reachable: {e}")

# 9. PYTHON PACKAGES
print("\n[9] Key Python packages")
pkgs = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "google-generativeai": "google.generativeai",
    "motor": "motor",
    "python-dotenv": "dotenv",
    "pymongo": "pymongo",
    "dnspython": "dns",
}
for name, imp in pkgs.items():
    try:
        parts = imp.split(".")
        mod = __import__(parts[0])
        for p in parts[1:]:
            mod = getattr(mod, p)
        ver = getattr(mod, "__version__", "installed")
        print(f"  OK {name}: {ver}")
    except ImportError:
        print(f"  MISSING {name}: NOT INSTALLED")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)

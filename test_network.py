"""Quick diagnostic: Can Python reach Google's Gemini API?"""
import socket, ssl, os, sys, time
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
print(f"API Key: {key[:12]}...")

# Test 1: DNS resolution
print("\n--- Test 1: DNS Resolution ---")
try:
    ips = socket.getaddrinfo("generativelanguage.googleapis.com", 443)
    print(f"OK: Resolved to {ips[0][4][0]}")
except Exception as e:
    print(f"FAIL: DNS resolution failed: {e}")
    sys.exit(1)

# Test 2: Raw TCP connection
print("\n--- Test 2: TCP Connection (port 443) ---")
try:
    s = socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=8)
    print(f"OK: TCP connected")
    s.close()
except Exception as e:
    print(f"FAIL: TCP connection failed: {e}")
    print("  -> Your firewall/ISP is blocking outbound TCP to Google's API servers.")
    sys.exit(1)

# Test 3: TLS/SSL handshake
print("\n--- Test 3: SSL Handshake ---")
try:
    ctx = ssl.create_default_context()
    s = socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=8)
    ss = ctx.wrap_socket(s, server_hostname="generativelanguage.googleapis.com")
    print(f"OK: SSL connected, version={ss.version()}")
    ss.close()
except ssl.SSLError as e:
    print(f"FAIL: SSL handshake failed: {e}")
    print("  -> Trying unverified SSL...")
    try:
        ctx2 = ssl._create_unverified_context()
        s2 = socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=8)
        ss2 = ctx2.wrap_socket(s2, server_hostname="generativelanguage.googleapis.com")
        print(f"OK with unverified: SSL version={ss2.version()}")
        ss2.close()
    except Exception as e2:
        print(f"FAIL even unverified: {e2}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)

# Test 4: HTTP GET to list models
print("\n--- Test 4: HTTP API Call ---")
import urllib.request, json
try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    ctx3 = ssl._create_unverified_context()
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=15, context=ctx3)
    data = json.loads(resp.read().decode("utf-8"))
    models = [m["name"] for m in data.get("models", []) if "flash" in m["name"]]
    print(f"OK: Got {len(data.get('models',[]))} models, flash models: {models[:3]}")
except Exception as e:
    print(f"FAIL: HTTP request failed: {e}")
    sys.exit(1)

print("\n=== ALL TESTS PASSED — Gemini API is reachable! ===")

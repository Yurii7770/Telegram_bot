import requests
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "DefiLlama"
print(f"=== Testing Direct Twitter APIs (FxTwitter & VxTwitter) for @{username} ===")

# Test VxTwitter / FxTwitter API
endpoints = [
    f"https://api.vxtwitter.com/{username}",
    f"https://api.fxtwitter.com/{username}",
    f"https://api.fixupx.com/{username}"
]

headers = {
    "User-Agent": "TelegramBot (like TwitterBot)"
}

for ep in endpoints:
    try:
        r = requests.get(ep, headers=headers, timeout=5)
        print(f"Endpoint {ep}: status {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            tweet = data.get("tweet") or data.get("user", {}).get("pinned_tweet")
            print(f"  Data: {json.dumps(data, ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

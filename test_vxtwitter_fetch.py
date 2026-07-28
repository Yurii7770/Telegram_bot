import requests
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "vitalikbuterin"
print(f"=== Testing VxTwitter & FxTwitter Timeline Extraction for @{username} ===")

url = f"https://api.vxtwitter.com/{username}"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

r = requests.get(url, headers=headers, timeout=5)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print("Keys in response:", list(data.keys()))
    print("JSON Snippet:", json.dumps(data, indent=2, ensure_ascii=False)[:500])

import requests
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "DefiLlama"
print(f"=== Testing Public Twitter Syndication & Embed API for @{username} ===")

url = f"https://cdn.syndication.twimg.com/widgets/timelines/user?screen_name={username}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=5)
print(f"Syndication status: {r.status_code}")
if r.status_code == 200:
    print("Response snippet:", r.text[:300])
else:
    # Try tweet embeds feed
    embed_url = f"https://syndication.twitter.com/tweets.json?ids=1890000000000000000"
    print("Testing embed endpoint...")

import sys
import io
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

accounts = ["DefiLlama", "MessariCrypto", "Lookonchain", "ArkhamIntel", "vitalikbuterin"]

print("=== Testing Tweet Details via FxTwitter / FixTweet ===")
for acc in accounts:
    # 1. Profile API
    url = f"https://api.fxtwitter.com/{acc}"
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            data = r.json()
            user = data.get("user", {})
            print(f"[{acc}] Name: {user.get('name')}, Tweets: {user.get('tweets')}")
    except Exception as e:
        print(f"[{acc}] Error: {e}")

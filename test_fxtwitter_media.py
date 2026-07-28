import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

accounts = ["Lookonchain", "DefiLlama", "ArkhamIntel", "MessariCrypto"]

for acc in accounts:
    r = requests.get(f"https://api.fxtwitter.com/{acc}", timeout=5)
    if r.status_code == 200:
        data = r.json().get("user", {})
        pinned = data.get("pinned_tweet")
        if pinned:
            media = pinned.get("media", {})
            photos = media.get("photos", []) if isinstance(media, dict) else []
            photo_urls = [p.get("url") for p in photos if isinstance(p, dict) and p.get("url")]
            print(f"@{acc} Pinned Tweet: {pinned.get('text', '')[:50]}... | Photos ({len(photo_urls)}): {photo_urls}")
        else:
            print(f"@{acc}: User data fetched OK, no pinned tweet media")
    else:
        print(f"@{acc}: Status {r.status_code}")

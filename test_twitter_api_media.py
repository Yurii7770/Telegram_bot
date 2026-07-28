import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

accounts = ["Lookonchain", "DefiLlama", "ArkhamIntel", "MessariCrypto"]

print("=== Testing Direct Tweet & Media Retrieval via FxTwitter/VxTwitter API ===")
for acc in accounts:
    try:
        url = f"https://api.vxtwitter.com/{acc}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            tweets = data.get("tweets", [])
            print(f"@{acc}: status 200, tweets count = {len(tweets)}")
            for tw in tweets[:3]:
                media_urls = tw.get("media_urls", [])
                print(f"  - Tweet {tw.get('id')}: '{tw.get('text', '')[:50]}...' | Media: {media_urls}")
        else:
            print(f"@{acc}: status {r.status_code}")
    except Exception as e:
        print(f"@{acc}: error {e}")

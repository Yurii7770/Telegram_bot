import sys
import io
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

accounts = ["DefiLlama", "MessariCrypto", "santimentfeed", "Lookonchain", "ArkhamIntel", "vitalikbuterin"]

bridges = [
    "https://rsshub.app/twitter/user/{acc}",
    "https://rsshub.rssforever.com/twitter/user/{acc}",
    "https://nitter.privacydev.net/{acc}/rss",
    "https://nitter.poast.org/{acc}/rss",
    "https://nitter.cz/{acc}/rss",
    "https://twitrss.me/twitter_user/?user={acc}"
]

print("=== Testing Twitter RSS Bridges ===")
for acc in accounts:
    found = False
    for b in bridges:
        url = b.format(acc=acc)
        try:
            r = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            if r.status_code == 200 and ("<rss" in r.text.lower() or "<feed" in r.text.lower() or "item" in r.text.lower()):
                print(f"[SUCCESS] [{acc}] via {url} (len={len(r.text)})")
                found = True
                break
        except Exception:
            pass
    if not found:
        print(f"[FAILED] [{acc}] No working unauthenticated RSS bridge found")

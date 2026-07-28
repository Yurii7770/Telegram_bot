import requests
import json
from bs4 import BeautifulSoup

print("=== Testing Syndication & Public APIs ===")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# 1. Syndication endpoint 1
for acc in ["DefiLlama", "DuneAnalytics", "vitalikbuterin"]:
    url = f"https://cdn.syndication.twimg.com/widgets-timeline/v2/{acc}?lang=en"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"[Syndication v2] {acc}: status={r.status_code}")
    except Exception as e:
        print(f"[Syndication v2] {acc}: {e}")

# 2. CryptoPanic API (free public news feed for crypto/DeFi/web3)
url_cp = "https://cryptopanic.com/api/v1/posts/?auth_token=free&public=true"
try:
    r = requests.get(url_cp, timeout=5)
    print(f"\n[CryptoPanic Public] status={r.status_code}")
    if r.status_code == 200:
        data = r.json()
        results = data.get("results", [])
        print(f"CryptoPanic returned {len(results)} items!")
        if results:
            print("Sample news:", results[0].get("title"), "| Source:", results[0].get("domain"))
except Exception as e:
    print(f"[CryptoPanic] Error: {e}")

# 3. Test CoinGecko / CoinMarketCap / CoinDesk RSS feeds
rss_urls = [
    ("CoinDesk RSS", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("CoinTelegraph RSS", "https://cointelegraph.com/rss"),
    ("Decrypt RSS", "https://decrypt.co/feed"),
    ("DeFi Pulse / Llama RSS", "https://defillama.com/news")
]

print("\n=== Testing RSS Feeds ===")
for name, url in rss_urls:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"[{name}] status={r.status_code}, len={len(r.text)}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

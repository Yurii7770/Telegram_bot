import sys
import io
import requests
import bs4
import urllib.parse

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

accounts = ["DefiLlama", "MessariCrypto", "elonmusk", "cz_binance", "zksync", "PancakeSwap", "Bitcoin"]

print("=== Testing Google News RSS for Target Accounts ===")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for acc in accounts:
    query = urllib.parse.quote(f"{acc} crypto")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = bs4.BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')[:3]
            print(f"[OK] [{acc}] Google News RSS found {len(items)} items!")
            if items:
                print(f"   Sample: {items[0].title.text}")
        else:
            print(f"[STATUS {r.status_code}] [{acc}]")
    except Exception as e:
        print(f"[ERROR] [{acc}]: {e}")

import requests
import json
from bs4 import BeautifulSoup

target_accounts = ["DefiLlama", "MessariCrypto", "santimentfeed", "Lookonchain", "ArkhamIntel", "vitalikbuterin"]

print("=== Testing Twitter Account Timeline Fetchers ===")

# Test 1: Syndication Timeline JS widget URL
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

for acc in target_accounts:
    # Test FixupX / FxTwitter / Twitter Syndication
    url = f"https://syndication.twitter.com/srv/timeline-profile/priv-user/{acc}"
    try:
        r = requests.get(url, timeout=5, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            next_data = soup.find('script', id='__NEXT_DATA__')
            if next_data:
                data = json.loads(next_data.string)
                entries = data.get('props', {}).get('pageProps', {}).get('timeline', {}).get('entries', [])
                print(f"[{acc}] Syndication found {len(entries)} entries!")
            else:
                print(f"[{acc}] Syndication status 200 but no NEXT_DATA")
        else:
            print(f"[{acc}] Syndication status={r.status_code}")
    except Exception as e:
        print(f"[{acc}] Syndication error: {e}")

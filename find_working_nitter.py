import requests
import bs4
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

nitter_instances = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.space",
    "https://nitter.cz"
]

account = "Lookonchain"

print(f"=== Searching Active Nitter RSS for @{account} ===")
for inst in nitter_instances:
    try:
        url = f"{inst}/{account}/rss"
        r = requests.get(url, timeout=4)
        if r.status_code == 200 and "<rss" in r.text.lower():
            soup = bs4.BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')
            print(f"✅ SUCCESS {inst}: found {len(items)} items!")
            for item in items[:2]:
                title = item.title.text if item.title else ""
                desc = item.description.text if item.description else ""
                desc_soup = bs4.BeautifulSoup(desc, 'html.parser')
                imgs = [img['src'] for img in desc_soup.find_all('img') if img.get('src')]
                print(f"   - Post: '{title[:50]}...' | Images: {imgs}")
            break
        else:
            print(f"❌ FAIL {inst}: status {r.status_code}")
    except Exception as e:
        print(f"❌ FAIL {inst}: {e}")

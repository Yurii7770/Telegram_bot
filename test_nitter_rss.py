import requests
import bs4
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "DefiLlama"
print(f"=== Testing Nitter RSS for Direct Twitter Posts (@{username}) ===")

nitter_instances = [
    f"https://nitter.poast.org/{username}/rss",
    f"https://nitter.privacydev.net/{username}/rss",
    f"https://nitter.cz/{username}/rss",
    f"https://nitter.space/{username}/rss"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for url in nitter_instances:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"Nitter instance {url.split('/')[2]}: Status {r.status_code}")
        if r.status_code == 200:
            soup = bs4.BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')[:3]
            print(f"✅ Found {len(items)} real tweets!")
            for item in items:
                title = item.title.text.strip() if item.title else ""
                link = item.link.text.strip() if item.link else ""
                # Convert nitter link to official x.com tweet link
                tweet_id = link.split('/')[-1].replace('#m', '')
                real_x_url = f"https://x.com/{username}/status/{tweet_id}"
                print(f"  - Real Tweet ID: {tweet_id} => {real_x_url}")
                print(f"    Text: '{title[:70]}...'")
            break
    except Exception as e:
        print(f"  Error: {e}")

import requests
import sys
import io
from bs4 import BeautifulSoup

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "DefiLlama"
url = f"https://syndication.twitter.com/srv/timeline-profile/priv/{username}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=10)
print(f"Syndication API status for @{username}: {r.status_code}")

if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        import json
        data = json.loads(next_data.string)
        entries = data.get('props', {}).get('pageProps', {}).get('timeline', {}).get('entries', [])
        print(f"Found {len(entries)} timeline entries!")
        for entry in entries[:5]:
            content = entry.get('content', {}).get('tweet', {})
            if content:
                tweet_id = content.get('id_str')
                text = content.get('full_text', content.get('text', ''))
                media = content.get('extended_entities', {}).get('media', []) or content.get('entities', {}).get('media', [])
                media_urls = [m.get('media_url_https') for m in media if m.get('media_url_https')]
                print(f"- Tweet {tweet_id}: '{text[:60]}...' | Media ({len(media_urls)}): {media_urls}")

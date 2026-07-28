import requests
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "DefiLlama"
url = f"https://cdn.syndication.twimg.com/widgets/timelines/user?screen_name={username}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print("Keys:", list(data.keys()))
    body = data.get("body", "")
    print(f"Body snippet length: {len(body)}")
    import bs4
    soup = bs4.BeautifulSoup(body, 'html.parser')
    tweets = soup.find_all('li', class_='timeline-Tweet')
    print(f"✅ Found {len(tweets)} tweets in Syndication timeline HTML!")
    for tw in tweets[:5]:
        tweet_id = tw.get('data-tweet-id')
        text_elem = tw.find('p', class_='timeline-Tweet-text')
        text = text_elem.text.strip() if text_elem else ""
        print(f"- Tweet #{tweet_id}: '{text[:70]}...'")
        print(f"  Direct Link: https://x.com/{username}/status/{tweet_id}")

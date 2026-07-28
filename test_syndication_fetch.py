import requests
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

username = "DefiLlama"
print(f"=== Testing Direct Twitter Syndication Fetch for @{username} ===")

url = f"https://syndication.twitter.com/srv/timeline-profile/history?screen_name={username}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    import bs4
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    # Extract __NEXT_DATA__ JSON script
    script = soup.find('script', id='__NEXT_DATA__')
    if script:
        data = json.loads(script.string)
        timeline = data.get('props', {}).get('pageProps', {}).get('timeline', {}).get('entries', [])
        print(f"✅ Found {len(timeline)} raw tweet entries!")
        for entry in timeline[:3]:
            tweet = entry.get('content', {}).get('tweet', {})
            if tweet:
                tweet_id = tweet.get('id_str')
                text = tweet.get('text')
                user = tweet.get('user', {}).get('screen_name')
                print(f"- Tweet ID: {tweet_id} | @{user}: '{text[:60]}...'")
                print(f"  URL: https://x.com/{user}/status/{tweet_id}")

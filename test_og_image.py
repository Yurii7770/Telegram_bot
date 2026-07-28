import requests
import bs4
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

test_urls = [
    "https://beincrypto.com",
    "https://crypto.news",
    "https://thedefiant.io"
]

print("=== Testing Open Graph Featured Image Extraction ===")
for url in test_urls:
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        og_image = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        img_url = og_image["content"] if og_image and og_image.get("content") else None
        print(f"URL: {url} => Featured Image: {img_url}")
    except Exception as e:
        print(f"URL: {url} => Error: {e}")

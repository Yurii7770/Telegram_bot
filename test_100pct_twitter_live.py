import sys
import io
import json
from config import Config
from content_fetcher import ContentFetcher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING 100% TWITTER-ONLY CONTENT FETCHER ===")
fetcher = ContentFetcher(Config.TWITTER_AUTH_TOKEN, Config.TWITTER_CT0)

target_accounts = ["DefiLlama", "vitalikbuterin"]
items = fetcher.fetch_all_sources(target_accounts)

print(f"✅ Fetched total {len(items)} items strictly from Twitter!")
for idx, item in enumerate(items):
    print(f"\n--- Item [{idx+1}] ---")
    print(f"Author: @{item['author']}")
    print(f"URL: {item['url']}")
    print(f"ID: {item['id']}")
    print(f"Text: '{item['text'][:80]}...'")
    print(f"Has Media: {item['has_media']} ({len(item['media_urls'])} photos)")

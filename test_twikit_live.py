import asyncio
import sys
import io
from config import Config
from content_fetcher import ContentFetcher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== Testing Twitter Twikit Fetch with New Cookies ===")
fetcher = ContentFetcher(Config.TWITTER_AUTH_TOKEN, Config.TWITTER_CT0)

print(f"Auth Token set: {Config.TWITTER_AUTH_TOKEN[:10]}...")
print(f"CT0 set: {Config.TWITTER_CT0[:10]}...")

tweets = fetcher.get_twitter_posts("DefiLlama", limit=3)
print(f"\nFetched {len(tweets)} tweets for @DefiLlama:")
for tw in tweets:
    print(f"ID: {tw['id']}")
    print(f"Author: @{tw['author']}")
    print(f"Title: {tw['title']}")
    print(f"Has Media: {tw['has_media']}")
    print(f"Media URLs: {tw['media_urls']}")
    print(f"Text snippet: {tw['text'][:100]}...\n")

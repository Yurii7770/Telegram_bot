import sys
import io
from config import Config
from database import Database
from content_fetcher import ContentFetcher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

db = Database(Config.DATABASE_PATH)
fetcher = ContentFetcher(Config.TWITTER_AUTH_TOKEN, Config.TWITTER_CT0)

items = fetcher.fetch_all_sources(Config.TARGET_ACCOUNTS, Config.RSS_FEEDS, Config.ENABLE_RSS_FEEDS)

print(f"Total items fetched from all sources: {len(items)}")
unprocessed = [item for item in items if not db.is_item_processed(item['id'])]
print(f"Unprocessed items count: {len(unprocessed)}")

for item in items[:10]:
    is_proc = db.is_item_processed(item['id'])
    print(f"Item [{item['id']}] (@{item['author']}): Processed={is_proc} - Title: {item['title'][:60]}")

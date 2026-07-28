import sys
import io
from config import Config
from twitter_poster import TwitterPoster

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING PLAYWRIGHT AUTOMATED TWITTER POSTER ===")
poster = TwitterPoster()

# Test with a live DefiLlama tweet or account status
print(f"Auth token set: {Config.TWITTER_AUTH_TOKEN[:10]}...")
print(f"CT0 set: {Config.TWITTER_CT0[:10]}...")

# We test the playwright posting module initialization
print("Playwright TwitterPoster module loaded and ready!")

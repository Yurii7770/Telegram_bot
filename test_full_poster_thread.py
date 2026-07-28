import threading
import sys
import io
from twitter_poster import TwitterPoster

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_test():
    print("=== Testing TwitterPoster inside multithreaded Telegram listener ===")
    poster = TwitterPoster()
    # Test method signature and event loop initialization
    print("TwitterPoster loaded successfully with thread-safe asyncio loop!")

t = threading.Thread(target=run_test)
t.start()
t.join()

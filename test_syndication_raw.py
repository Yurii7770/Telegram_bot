import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

url = "https://cdn.syndication.twimg.com/widgets/timelines/user?screen_name=DefiLlama"
r = requests.get(url, timeout=5)
print(f"Status: {r.status_code}, Length: {len(r.text)}")
print(f"Content snippet: '{r.text[:200]}'")

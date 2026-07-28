import requests
from bs4 import BeautifulSoup
import json

print("--- Testing Nitter & RSS instances ---")
instances = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.lucabased.xyz",
    "https://rsshub.app/twitter/user/DefiLlama",
    "https://twitrss.me/twitter_user/?user=DefiLlama",
]

for inst in instances:
    try:
        if "rss" in inst or "twitrss" in inst:
            r = requests.get(inst, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            print(f"[{inst}] status={r.status_code}, len={len(r.text)}")
        else:
            url = f"{inst}/DefiLlama/rss"
            r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            print(f"[Nitter RSS: {inst}] status={r.status_code}, len={len(r.text)}")
    except Exception as e:
        print(f"[{inst}] Error: {e}")

print("\n--- Testing Twikit (Guest or Cookie) ---")
try:
    from twikit import Client
    client = Client('en-US')
    # Let's see if guest login or search works
    print("Twikit client initialized.")
except Exception as e:
    print(f"Twikit error: {e}")

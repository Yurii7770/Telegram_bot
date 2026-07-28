import requests
import json
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

session = requests.Session()
auth_token = Config.TWITTER_AUTH_TOKEN
ct0 = Config.TWITTER_CT0

session.cookies.set("auth_token", auth_token, domain=".x.com")
session.cookies.set("ct0", ct0, domain=".x.com")

headers = {
    "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7T244GcvTudu1HeS2BkDtxq2W08g50w5g50w5g50w",
    "x-csrf-token": ct0,
    "x-twitter-auth-type": "OAuth2Session",
    "x-twitter-active-user": "yes",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "content-type": "application/json"
}

print("=== Testing Twitter Web Session Verification ===")
# Try fetching home timeline or user info to test session auth
r = session.get("https://x.com/i/api/1.1/account/verify_credentials.json", headers=headers, timeout=10)
print(f"Verify credentials status: {r.status_code}")
if r.status_code == 200:
    user_data = r.json()
    print(f"✅ Authenticated as Twitter user: @{user_data.get('screen_name')} (Name: {user_data.get('name')})")
else:
    print(f"Response: {r.text[:200]}")

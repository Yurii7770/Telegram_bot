import requests
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

auth_token = Config.TWITTER_AUTH_TOKEN
ct0 = Config.TWITTER_CT0
twid = Config.TWITTER_TWID

print(f"Auth Token: {auth_token[:10]}...")
print(f"CT0: {ct0[:10]}...")
print(f"TWID: {twid}")

headers = {
    "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7T244GcvTudu1HeS2BkDtxq2W08g50w5g50w5g50w",
    "x-csrf-token": ct0,
    "cookie": f"auth_token={auth_token}; ct0={ct0}; twid={twid}",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "x-twitter-active-user": "yes",
    "x-twitter-auth-type": "OAuth2Session"
}

r = requests.get("https://x.com/i/api/1.1/account/verify_credentials.json", headers=headers, timeout=10)
print(f"Verify credentials status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"✅ Authenticated as Twitter user: @{data.get('screen_name')} (ID: {data.get('id_str')})")
else:
    print(f"Response: {r.text[:200]}")

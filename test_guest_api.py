import requests
import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== Testing Official Twitter Guest API for 100% Direct Tweet Fetching ===")

session = requests.Session()
BEARER = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7T244GcvTudu1HeS2BkDtxq2W08g50w5g50w5g50w"

# 1. Activate Guest Token
guest_resp = session.post(
    "https://api.twitter.com/1.1/guest/activate.json",
    headers={"Authorization": BEARER},
    timeout=5
)
print(f"Guest Token status: {guest_resp.status_code}")
if guest_resp.status_code == 200:
    guest_token = guest_resp.json().get("guest_token")
    print(f"✅ Guest Token acquired: {guest_token}")
    
    # 2. Fetch User Profile / Tweet Timeline
    username = "DefiLlama"
    headers = {
        "Authorization": BEARER,
        "x-guest-token": guest_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # GraphQL UserByScreenName
    url = f"https://x.com/i/api/graphql/sLVLhkWC283v29uD0Z-ioQ/UserByScreenName?variables=%7B%22screen_name%22%3A%22{username}%22%7D"
    user_r = session.get(url, headers=headers, timeout=5)
    print(f"UserByScreenName status: {user_r.status_code}")
    if user_r.status_code == 200:
        data = user_r.json()
        print("User data snippet:", json.dumps(data, ensure_ascii=False)[:300])

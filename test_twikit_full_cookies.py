import asyncio
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Twikit with Full Cookies Dictionary ===")
    from twikit import Client
    client = Client('en-US')
    
    cookies = {
        'auth_token': Config.TWITTER_AUTH_TOKEN,
        'ct0': Config.TWITTER_CT0,
        'guest_id': 'v1%3A170000000000000000'
    }
    client.set_cookies(cookies)
    
    try:
        # Try fetching account user or timeline
        print(f"Auth token prefix: {Config.TWITTER_AUTH_TOKEN[:10]}...")
        user = await client.get_user_by_screen_name('DefiLlama')
        print(f"SUCCESS: Connected! User screen name: @{user.screen_name}, ID: {user.id}")
    except Exception as e:
        print(f"Twikit error: {e}")

asyncio.run(main())

import asyncio
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    try:
        from twikit import Client
        client = Client('en-US')
        client.set_cookies({
            'auth_token': Config.TWITTER_AUTH_TOKEN,
            'ct0': Config.TWITTER_CT0
        })
        print(f"Testing Twikit client with fresh cookies...")
        # Get user account info
        user = await client.get_user_by_screen_name('DefiLlama')
        print(f"Successfully connected! Target User ID: {user.id}")
    except Exception as e:
        print(f"Twikit test error: {e}")

asyncio.run(main())

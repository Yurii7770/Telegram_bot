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
        user = await client.get_user_by_screen_name('DefiLlama')
        print(f"User ID for @DefiLlama: {user.id}")
        tweets = await user.get_tweets('Tweets', count=3)
        print(f"Fetched {len(tweets)} tweets!")
        for tw in tweets:
            media = tw.media if hasattr(tw, 'media') else []
            print(f"- Tweet {tw.id}: '{tw.text[:60]}...' | Media: {media}")
    except Exception as e:
        print(f"Twikit error: {e}")

asyncio.run(main())

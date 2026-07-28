import asyncio
from twikit import Client

async def main():
    client = Client('en-US')
    try:
        # Load user by screen name
        user = await client.get_user_by_screen_name('DefiLlama')
        print(f"User found: {user.name} ({user.id})")
        tweets = await user.get_tweets('Tweets', count=5)
        print(f"Fetched {len(tweets)} tweets via Twikit:")
        for t in tweets:
            print(f"- [{t.id}] {t.text[:100]}...")
    except Exception as e:
        print(f"Twikit fetch error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

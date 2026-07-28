import asyncio
from twikit import Client

async def test_cookies(auth_token, ct0):
    client = Client('en-US')
    cookies = {
        'auth_token': auth_token,
        'ct0': ct0
    }
    client.set_cookies(cookies)
    try:
        user = await client.get_user_by_screen_name('DefiLlama')
        print(f"Success! Fetched user: {user.name}")
        tweets = await user.get_tweets('Tweets', count=3)
        for t in tweets:
            print(f"- {t.text[:80]}...")
    except Exception as e:
        print(f"Cookie fetch failed: {e}")

if __name__ == "__main__":
    print("Testing Twikit cookie method with dummy or provided cookies")

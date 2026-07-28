import asyncio
import sys
import io
from datetime import datetime, timezone, timedelta

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Playwright Tweet Timestamp & Max-Age Filter (4 hours) ===")
    from playwright.async_api import async_playwright
    from config import Config
    
    username = "DefiLlama"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        if Config.TWITTER_AUTH_TOKEN and Config.TWITTER_CT0:
            cookies = [
                {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"},
                {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"}
            ]
            await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(f"https://x.com/{username}", timeout=30000)
        await page.wait_for_timeout(4000)
        
        tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
        print(f"Total tweets on page: {len(tweet_elements)}")
        
        for idx, el in enumerate(tweet_elements[:5]):
            time_el = await el.query_selector('time')
            datetime_str = await time_el.get_attribute('datetime') if time_el else ""
            
            if datetime_str:
                tweet_dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_hours = (now - tweet_dt).total_seconds() / 3600.0
                
                print(f"Tweet [{idx+1}]: Published {datetime_str} ({age_hours:.1f} hours ago)")
                if age_hours > 4.0:
                    print(f"  ❌ DISCARDED: Tweet is older than 4 hours ({age_hours:.1f}h ago)")
                else:
                    print(f"  ✅ KEPT: Fresh tweet ({age_hours:.1f}h ago)")
                    
        await browser.close()

asyncio.run(main())

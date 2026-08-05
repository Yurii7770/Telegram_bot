import asyncio
import sys
import io
from datetime import datetime, timezone

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    from playwright.async_api import async_playwright
    from config import Config
    
    accounts = ["DefiLlama", "Lookonchain", "ArkhamIntel", "vitalikbuterin"]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        if Config.TWITTER_AUTH_TOKEN and Config.TWITTER_CT0:
            await context.add_cookies([
                {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
                {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"}
            ])
        page = await context.new_page()
        
        for acc in accounts:
            print(f"\n--- Checking @{acc} ---")
            await page.goto(f"https://x.com/{acc}", timeout=25000)
            await page.wait_for_timeout(3000)
            tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
            print(f"Total tweets found on page: {len(tweet_elements)}")
            
            for idx, el in enumerate(tweet_elements[:3]):
                link_el = await el.query_selector('a[href*="/status/"]')
                link = await link_el.get_attribute("href") if link_el else ""
                text_el = await el.query_selector('div[data-testid="tweetText"]')
                text = await text_el.inner_text() if text_el else ""
                time_el = await el.query_selector('time')
                datetime_str = await time_el.get_attribute('datetime') if time_el else ""
                
                age_hours = -1
                if datetime_str:
                    tweet_dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    age_hours = (now - tweet_dt).total_seconds() / 3600.0
                
                print(f"  [{idx+1}] Age: {age_hours:.1f}h | Date: {datetime_str} | Text: '{text[:50]}...'")
                print(f"      Passed 4h filter? {age_hours >= 0 and age_hours <= 4.0}")
                
        await browser.close()

asyncio.run(main())

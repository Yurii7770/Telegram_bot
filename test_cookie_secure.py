import asyncio
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Playwright Cookie Injection with Secure & SameSite ===")
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        
        cookies = [
            {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"},
            {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"}
        ]
        if Config.TWITTER_TWID:
            cookies.append({"name": "twid", "value": Config.TWITTER_TWID, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"})
            
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        print("Navigating to https://x.com/home...")
        await page.goto("https://x.com/home", timeout=30000)
        await page.wait_for_timeout(4000)
        
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")
        
        # Check if home feed or tweet textarea loaded
        textarea = await page.query_selector('div[data-testid="tweetTextarea_0"], div[contenteditable="true"]')
        if textarea:
            print("✅ SUCCESS: Playwright authenticated to Twitter home timeline & found tweet textarea!")
        else:
            print("⚠️ Home timeline loaded, searching for tweet buttons...")
            buttons = await page.query_selector_all('button, div[role="button"]')
            for btn in buttons[:10]:
                testid = await btn.get_attribute("data-testid")
                txt = await btn.inner_text()
                if testid or txt:
                    print(f"Button: testid='{testid}', text='{txt.strip()[:20]}'")
                    
        await browser.close()

asyncio.run(main())

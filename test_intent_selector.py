import asyncio
import sys
import io
import urllib.parse
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Playwright Twitter Compose / Post Selectors ===")
    from playwright.async_api import async_playwright
    
    text = urllib.parse.quote("Testing automated post creation")
    target_url = f"https://x.com/intent/tweet?text={text}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        await context.add_cookies([
            {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"},
            {"name": "twid", "value": Config.TWITTER_TWID, "domain": ".x.com", "path": "/"}
        ])
        page = await context.new_page()
        print(f"Navigating to {target_url}...")
        await page.goto(target_url, timeout=30000)
        await page.wait_for_timeout(4000)
        
        print(f"Current page URL: {page.url}")
        print(f"Current page title: {await page.title()}")
        
        # Search for buttons on page
        buttons = await page.query_selector_all('button, div[role="button"]')
        print(f"Found {len(buttons)} interactive buttons/elements on page.")
        
        for idx, btn in enumerate(buttons[:15]):
            testid = await btn.get_attribute("data-testid")
            btn_text = await btn.inner_text()
            if testid or btn_text:
                print(f"Button [{idx}]: testid='{testid}', text='{btn_text.strip()[:30]}'")
                
        await browser.close()

asyncio.run(main())

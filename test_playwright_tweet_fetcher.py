import asyncio
import sys
import io
import json

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Playwright Direct Twitter Timeline Extractor ===")
    from playwright.async_api import async_playwright
    from config import Config
    
    username = "DefiLlama"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        await context.add_cookies([
            {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"}
        ])
        page = await context.new_page()
        
        target_url = f"https://x.com/{username}"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url, timeout=30000)
        await page.wait_for_timeout(4000)
        
        # Extract tweet articles
        tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
        print(f"✅ Found {len(tweet_elements)} live tweets on @{username}'s timeline!")
        
        tweets = []
        for el in tweet_elements[:5]:
            # Extract status link
            link_el = await el.query_selector('a[href*="/status/"]')
            link = await link_el.get_attribute("href") if link_el else ""
            if link and not link.startswith("http"):
                link = f"https://x.com{link}"
                
            # Extract tweet text
            text_el = await el.query_selector('div[data-testid="tweetText"]')
            text = await text_el.inner_text() if text_el else ""
            
            # Extract media images if present
            img_els = await el.query_selector_all('div[data-testid="tweetPhoto"] img')
            media_urls = []
            for img in img_els:
                src = await img.get_attribute("src")
                if src and "media" in src:
                    media_urls.append(src)
                    
            if link and text:
                tweet_id = link.split("/status/")[-1].split("?")[0]
                tweets.append({
                    "id": f"tw_{tweet_id}",
                    "author": username,
                    "title": f"Tweet by @{username}",
                    "text": text.strip(),
                    "url": link,
                    "has_media": len(media_urls) > 0,
                    "media_urls": media_urls
                })
                print(f"- ID: {tweet_id}")
                print(f"  URL: {link}")
                print(f"  Text: '{text.strip()[:60]}...'")
                print(f"  Media: {len(media_urls)} photos\n")
                
        await browser.close()

asyncio.run(main())

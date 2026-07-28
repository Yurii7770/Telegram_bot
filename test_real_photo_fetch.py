import asyncio
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Real Twitter Photo Extraction for @DefiLlama with Scroll ===")
    from playwright.async_api import async_playwright
    from config import Config
    from telegram_publisher import TelegramPublisher

    username = "DefiLlama"
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
        await context.add_cookies(cookies)

        page = await context.new_page()
        print(f"Navigating to https://x.com/{username}...")
        await page.goto(f"https://x.com/{username}", timeout=30000)
        await page.wait_for_timeout(5000)
        await page.evaluate("window.scrollBy(0, 500)")
        await page.wait_for_timeout(2000)

        tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
        print(f"Found {len(tweet_elements)} tweets for @{username}")
        for idx, el in enumerate(tweet_elements):
            img_els = await el.query_selector_all('div[data-testid="tweetPhoto"] img')
            print(f"Tweet [{idx+1}]: {len(img_els)} img elements")
            for img in img_els:
                src = await img.get_attribute("src")
                print(f"  Src: {src}")
                if src and "media" in src:
                    print(f"✅ Real Photo URL: {src}")
                    publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)
                    res = publisher.send_admin_preview(
                        db_id=8888,
                        title="🚨 <b>REAL TWITTER PHOTO PREVIEW</b>",
                        post_text=f"Testing real photo from @{username}",
                        author=username,
                        has_media=True,
                        media_urls=[src],
                        sniper_reply="Whale alert!",
                        target_platform="BOTH",
                        ai_opinion="Отличный скриншот китов",
                        source_url="https://x.com"
                    )
                    print(f"Delivered to Telegram: {res}")
                    await browser.close()
                    return

        await browser.close()

asyncio.run(main())

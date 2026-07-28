import sys
import io
import requests
import json
from config import Config
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

# Sample real news item from target account DuneAnalytics
sample_item = {
    "url": "https://x.com/DuneAnalytics/status/1880000000000000000",
    "author": "DuneAnalytics",
    "title": "Dune Analytics slashes 25% of workforce to pivot towards AI and institutional data",
    "text": "Dune Analytics has announced a strategic restructuring, cutting 25% of its workforce to reallocate capital towards AI-driven SQL analytics and institutional enterprise offerings."
}

# 3 Editorial Style Variants to test
styles = [
    {
        "name": "STYLE 1: Executive Punchy (Crisp & High-Density)",
        "prompt_tone": "Write a 2-paragraph punchy executive briefing. Zero fluff. Bold key terms.",
        "title": "⚡ <b>Dune Analytics cuts 25% of staff in <a href=\"{url}\">strategic AI pivot</a></b>",
        "post_text": "<b>Dune Analytics</b> is restructuring its workforce by reducing headcount by <b>25%</b> to aggressively reallocate capital toward AI-powered SQL data tools and institutional services.\n\n• <b>AI Reallocation</b>: Shifting engineering focus to automated natural-language queries.\n• <b>Institutional Focus</b>: Expanding enterprise-grade analytics pipelines for institutional funds."
    },
    {
        "name": "STYLE 2: Institutional Market Brief (Data-First & Dynamic)",
        "prompt_tone": "Write an authoritative market intelligence note. Focus on strategic impact.",
        "title": "📈 <b>Dune Analytics announces 25% workforce reduction to <a href=\"{url}\">scale enterprise AI infrastructure</a></b>",
        "post_text": "On-chain data giant <b>Dune Analytics</b> has initiated a <b>25% staff reduction</b> as part of an institutional pivot toward AI-assisted analytics and enterprise data infrastructure.\n\nKey takeaways:\n• <b>Resource Shift</b>: Capital is being redirected toward automated SQL synthesis and high-frequency data pipelines.\n• <b>Market Positioning</b>: Target expansion into institutional-grade DeFi and L2 analytics."
    },
    {
        "name": "STYLE 3: Direct Impact Flash (Ultra-Concise Bullet Lead)",
        "prompt_tone": "Write an ultra-condensed flash update. 1 sentence lead + 2 sharp bullets.",
        "title": "🚨 <b>Dune Analytics slashes headcount by 25% in <a href=\"{url}\">AI analytics restructuring</a></b>",
        "post_text": "<b>Dune Analytics</b> has cut <b>25% of its workforce</b> to focus capital on AI-driven data products and institutional enterprise solutions.\n\n• <b>Capital Shift</b>: Accelerating development of natural-language SQL engines.\n• <b>Enterprise Focus</b>: Strengthening dedicated infrastructure for institutional clients."
    }
]

print("=== Sending 3 Editorial Style Options to Telegram ===")

for i, st in enumerate(styles, 1):
    title_formatted = st["title"].replace("{url}", sample_item["url"])
    header = f"🧪 <b>[ТЕСТОВЫЙ ВАРИАНТ СТИЛЯ #{i}: {st['name']}]</b>\n\n"
    full_msg = f"{header}{title_formatted}\n\n{st['post_text']}"
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.ADMIN_CHAT_ID,
        "text": full_msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload, timeout=10)
    print(f"Option #{i} sent to Telegram: status={r.status_code}")


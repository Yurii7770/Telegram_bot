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

sample_item = {
    "url": "https://x.com/DuneAnalytics/status/1880000000000000000",
    "author": "DuneAnalytics"
}

# 2 Complete Style Options with Concluding Bottom Line
complete_styles = [
    {
        "name": "Complete Option 1: Executive Briefing + Bottom Line Verdict",
        "title": "⚡ <b>Dune Analytics slashes 25% of staff in <a href=\"{url}\">strategic AI restructuring</a></b>",
        "post_text": "On-chain data giant <b>Dune Analytics</b> is reducing headcount by <b>25%</b> to aggressively reallocate capital toward AI-powered SQL tools and enterprise analytics.\n\n• <b>AI Reallocation</b>: Shifting engineering resources toward automated natural-language database engines.\n• <b>Institutional Focus</b>: Expanding specialized data pipelines for institutional funds and protocols.\n\n💡 <b>Bottom Line:</b> Dune joins a growing wave of crypto infrastructure providers trimming legacy roles to double down on AI-native analytics capabilities."
    },
    {
        "name": "Complete Option 2: Market Briefing + Strategic Takeaway",
        "title": "🚨 <b>Dune Analytics cuts 25% of workforce to <a href=\"{url}\">scale enterprise AI infrastructure</a></b>",
        "post_text": "<b>Dune Analytics</b> has initiated a <b>25% staff reduction</b> as part of an institutional pivot toward AI-assisted analytics and enterprise infrastructure.\n\n• <b>Resource Shift</b>: Capital is being redirected toward automated SQL synthesis and high-frequency data pipelines.\n• <b>Enterprise Focus</b>: Target expansion into institutional-grade DeFi and Layer-2 analytics.\n\n🎯 <b>Strategic Outlook:</b> The move signals a broader shift across Web3 data platforms toward leaner teams focused heavily on AI-assisted user workflows."
    }
]

print("=== Sending 2 Complete Style Variants to Telegram ===")

for i, st in enumerate(complete_styles, 1):
    title_formatted = st["title"].replace("{url}", sample_item["url"])
    header = f"✨ <b>[ОБНОВЛЕННЫЙ ЗАВЕРШЕННЫЙ СТИЛЬ #{i}: {st['name']}]</b>\n\n"
    full_msg = f"{header}{title_formatted}\n\n{st['post_text']}"
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.ADMIN_CHAT_ID,
        "text": full_msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload, timeout=10)
    print(f"Complete Option #{i} sent to Telegram: status={r.status_code}")

import sys
import io
import requests
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sample_url = "https://x.com/DuneAnalytics/status/1880000000000000000"

# 2 Vibrant Attention-Grabbing Options with High-Density Emojis & Rich Formatting
vibrant_options = [
    {
        "name": "OPTION 1: High-Impact Breaking Flash (Emojis + Code Metrics + Punchy Lead)",
        "title": "🚨 <b>BREAKING: Dune Analytics <a href=\"{url}\">Slashes 25% of Staff</a> in Massive AI Pivot!</b>",
        "post_text": "💥 On-chain giant <b>Dune Analytics</b> just announced a <code>25% workforce reduction</code> to aggressively shift capital toward <i>AI-powered SQL engines</i> and enterprise data pipelines.\n\n📌 <b>Key Strategic Moves:</b>\n• 🤖 <b>AI Reallocation:</b> Shifting core engineering into <code>natural-language database copilots</code>.\n• 🏦 <b>Institutional Push:</b> Building high-frequency <i>enterprise data tools</i> for institutional funds.\n\n🎯 <b>The Big Picture:</b> <i>Major Web3 platforms are actively trimming legacy operational costs to fund AI-native analytics capabilities!</i>"
    },
    {
        "name": "OPTION 2: Ultra-Vibrant Crypto Insider (Bold Emojis + Multi-Tag Formatting)",
        "title": "💥 <b>MAJOR SHIFT: Dune Analytics <a href=\"{url}\">Cuts 25% of Workforce</a> to Double Down on AI!</b>",
        "post_text": "⚡ <b>Dune Analytics</b> is executing a major <code>25% headcount cut</code>, redirecting resources directly into <i>AI-driven database engines</i> and <code>institutional data feeds</code>.\n\n📊 <b>Core Highlights:</b>\n• 🚀 <b>AI Copilot Shift:</b> Doubling down on <code>automated SQL synthesis</code> for seamless queries.\n• 💼 <b>Enterprise Focus:</b> Expanding dedicated infrastructure for <i>institutional DeFi & L2 protocols</i>.\n\n💡 <i>This massive reallocation marks a defining trend as crypto data providers streamline teams to dominate the AI analytics race!</i>"
    }
]

print("=== Sending 2 Vibrant Style Options to Telegram ===")

for i, opt in enumerate(vibrant_options, 1):
    title_formatted = opt["title"].replace("{url}", sample_url)
    header = f"🔥 <b>[ЯРКИЙ «КРИЧАЩИЙ» СТИЛЬ #{i}: {opt['name']}]</b>\n\n"
    full_msg = f"{header}{title_formatted}\n\n{opt['post_text']}"
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.ADMIN_CHAT_ID,
        "text": full_msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload, timeout=10)
    print(f"Vibrant Option #{i} sent to Telegram: status={r.status_code}")

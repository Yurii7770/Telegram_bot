import sys
import io
import json
from config import Config
from ai_editor import AIEditor

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)

recent_topics = [
    "🚨 BREAKING: Dune Analytics Slashes 25% of Staff in AI Pivot!",
    "⚡ JUST IN: Vitalik Buterin Endorses FOCIL for Ethereum Upgrade"
]

duplicate_item = {
    "id": "test_dup_001",
    "author": "CoinTelegraph",
    "title": "Dune Analytics Lays Off 25% of Workforce to Focus on AI Data Engines",
    "text": "Crypto data provider Dune Analytics has cut a quarter of its workforce as it redirects capital into AI database copilots.",
    "url": "https://cointelegraph.com/news/dune-analytics-layoffs-ai"
}

new_unique_item = {
    "id": "test_unique_001",
    "author": "MessariCrypto",
    "title": "Messari Releases State of Solana Q1 2026 Report",
    "text": "Messari's latest Q1 2026 report shows Solana DEX volume surgin 150% quarter over quarter.",
    "url": "https://messari.io/report/state-of-solana"
}

print("=== Test 1: Processing Duplicate Story ===")
res1 = editor.process_item(duplicate_item, recent_topics=recent_topics)
print("Duplicate item result:", json.dumps(res1, indent=2, ensure_ascii=False))

print("\n=== Test 2: Processing Unique New Story ===")
res2 = editor.process_item(new_unique_item, recent_topics=recent_topics)
print("Unique item result:", json.dumps(res2, indent=2, ensure_ascii=False))

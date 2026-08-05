import os
from card_generator import CardGenerator

def test_generate():
    title = "🚨 BREAKING: Arkham Intel Denies Exchange Closure, Launches Decentralized Platform!"
    category = "📊 ON-CHAIN METRICS"
    bullets = [
        "• Volume Surge: Over $45M in $ARKM volume tracked within 2 hours",
        "• Platform Shift: Abandoning centralized exchange for decentralized protocols",
        "• Market Impact: Token price spiked +18% following announcement"
    ]
    
    card_bytes = CardGenerator.create_card(
        title=title,
        category=category,
        bullets=bullets,
        watermark_text="@CryptoInsight"
    )

    out_path = "test_generated_card.jpg"
    with open(out_path, "wb") as f:
        f.write(card_bytes)

    print(f"Generated test card successfully! Size: {len(card_bytes)} bytes. Saved to {out_path}")
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 5000

if __name__ == "__main__":
    test_generate()

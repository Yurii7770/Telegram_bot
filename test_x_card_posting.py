import os
import tempfile
import time
from card_generator import CardGenerator

def test_card_generation_flow():
    title = "⚡ JUST IN: Solana TVL Surges Past $5.2B as DePIN Protocols Skyrocket!"
    bullets = [
        "• TVL Growth: Up +24% over the last 7 days driven by Jupiter and Raydium",
        "• Active Wallets: Daily active addresses hit new ATH at 1.8M",
        "• Token Impact: $SOL touches $185 resistance level with massive spot volume"
    ]
    
    # Test card generation
    card_bytes = CardGenerator.create_card(
        title=title,
        category="📊 ON-CHAIN METRICS",
        bullets=bullets,
        watermark_text="@CryptoMaster"
    )

    tf = os.path.join(tempfile.gettempdir(), f"test_solana_card_{int(time.time())}.jpg")
    with open(tf, "wb") as f:
        f.write(card_bytes)

    print(f"Card successfully generated: {tf} ({len(card_bytes)} bytes)")
    assert os.path.exists(tf)
    assert len(card_bytes) > 10000

    # Cleanup test file
    if os.path.exists(tf):
        os.remove(tf)

if __name__ == "__main__":
    test_card_generation_flow()

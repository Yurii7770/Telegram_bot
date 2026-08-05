import os
from card_generator import CardGenerator

def test_creth_card():
    title = "Solana Ecosystem TVL Surges Past $5.2B as DePIN Volume Skyrockets"
    
    card_bytes = CardGenerator.create_card(
        title=title,
        category="CRETH",
        watermark_text="@CRETH"
    )

    out_path = "test_creth_minimal_card.jpg"
    with open(out_path, "wb") as f:
        f.write(card_bytes)

    print(f"Minimal @CRETH card generated! Size: {len(card_bytes)} bytes. Saved to {out_path}")
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 5000

if __name__ == "__main__":
    test_creth_card()

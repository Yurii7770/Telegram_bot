import os
import io
import sys
import unittest
from PIL import Image

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from database import Database
from watermark_processor import apply_watermark
from ai_editor import AIEditor
from config import Config

class TestAnalyticsAndWatermark(unittest.TestCase):
    def setUp(self):
        import uuid
        self.db_file = f"test_analytics_temp_{uuid.uuid4().hex[:8]}.db"
        self.db = Database(self.db_file)

    def tearDown(self):
        try:
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
        except Exception:
            pass

    def test_watermark_processor(self):
        """Tests that watermark processor successfully overlays text onto an image."""
        # Create a sample RGB image (400x300 red image)
        img = Image.new("RGB", (400, 300), color="red")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        # Apply watermark
        watermarked_bytes = apply_watermark(raw_bytes, "@TestCryptoChannel")
        self.assertIsNotNone(watermarked_bytes)
        self.assertGreater(len(watermarked_bytes), 1000)

        # Verify image can be opened after watermarking
        result_img = Image.open(io.BytesIO(watermarked_bytes))
        self.assertEqual(result_img.size, (400, 300))
        print("✅ Watermark Processor Test Passed!")

    def test_database_analytics_and_cost(self):
        """Tests LLM cost logging and analytics summary aggregation."""
        # Log sample LLM costs
        self.db.log_llm_cost("item_1", "claude-3.5-sonnet", 500, 200, 0.00105)
        self.db.log_llm_cost("item_2", "claude-3.5-sonnet", 600, 300, 0.00135)

        # Save pending and published posts
        db_id_1 = self.db.save_pending_post("item_1", "DefiLlama", "Title 1", "Body 1", False, [], [])
        db_id_2 = self.db.save_pending_post("item_2", "Lookonchain", "Title 2", "Body 2", False, [], [])

        self.db.update_pending_post_status(db_id_1, "PUBLISHED")
        self.db.record_published_message(db_id_1, telegram_message_id=9991)
        self.db.update_post_views(telegram_message_id=9991, views_count=1450)

        summary = self.db.get_analytics_summary()
        self.assertEqual(summary["total_items"], 2)
        self.assertEqual(summary["published_items"], 1)
        self.assertEqual(summary["total_views"], 1450)
        self.assertGreater(summary["total_cost_usd"], 0)
        print(f"✅ Database Analytics Test Passed! Summary: {summary}")

    def test_referral_links_injection(self):
        """Tests automatic referral links injection for partner keywords."""
        ai = AIEditor(openrouter_key="")
        sample_text = "Check out the volume surge on Bybit and Uniswap today!"
        result_text = ai._inject_referral_links(sample_text)
        
        self.assertIn("href=", result_text)
        self.assertIn("Bybit", result_text)
        self.assertIn("Uniswap", result_text)
        print(f"✅ Referral Links Injection Test Passed! Result: {result_text}")

if __name__ == "__main__":
    unittest.main()

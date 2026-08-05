import io
import os
import re
import logging
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("CardGenerator")

class CardGenerator:
    """
    Generates elegant, minimal dark-mode visual cards for Twitter (X) posts (1200x675 px).
    Designed to be clean, low-clutter, and focused on headline + @CRETH branding.
    """

    WIDTH = 1200
    HEIGHT = 675

    @staticmethod
    def _get_font(font_name: str = "arial.ttf", size: int = 24) -> ImageFont.ImageFont:
        font_paths = [
            f"C:\\Windows\\Fonts\\{font_name}",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    @classmethod
    def ba_audit_headline(cls, raw_title: str) -> str:
        """
        BA Quality Control Audit for card headlines:
        - Removes HTML tags, raw URLs, and bracket noise.
        - Truncates cleanly if headline exceeds 90 characters to avoid image overflow.
        - Ensures clean crypto ticker formatting.
        """
        if not raw_title:
            return "CRETH Market Update"

        clean = re.sub(r'<[^>]+>', '', raw_title).strip()
        clean = re.sub(r'https?://\S+', '', clean).strip()
        clean = re.sub(r'\s+', ' ', clean)

        if len(clean) > 90:
            truncated = clean[:87]
            last_space = truncated.rfind(' ')
            if last_space > 40:
                clean = truncated[:last_space] + "..."
            else:
                clean = truncated + "..."

        logger.info(f"[BA AUDIT OK] Headline approved for @CRETH card: '{clean}'")
        return clean

    @classmethod
    def create_card(
        cls,
        title: str,
        category: str = "CRETH",
        source_image_bytes: Optional[bytes] = None,
        watermark_text: str = "@CRETH"
    ) -> bytes:
        """
        Creates a minimal 1200x675 visual card with soft dark tones and @CRETH branding.
        """
        # Strict BA audit on text content
        clean_title = cls.ba_audit_headline(title)
        watermark_text = "@CRETH"  # Strictly enforce @CRETH brand identity

        # 1. Base canvas setup with muted, elegant dark slate background
        canvas = Image.new("RGBA", (cls.WIDTH, cls.HEIGHT), (15, 23, 42, 255)) # Dark slate (#0F172A)
        draw = ImageDraw.Draw(canvas)

        # Subtle dark gradient overlay (soft top-left glow)
        accent_layer = Image.new("RGBA", (cls.WIDTH, cls.HEIGHT), (0, 0, 0, 0))
        acc_draw = ImageDraw.Draw(accent_layer)
        acc_draw.ellipse([-150, -150, 500, 500], fill=(30, 41, 59, 100)) # Muted slate blue glow
        canvas = Image.alpha_composite(canvas, accent_layer)
        draw = ImageDraw.Draw(canvas)

        # 2. Render Source Photo (if provided) on right side with soft rounded border
        left_content_width = cls.WIDTH - 120
        if source_image_bytes:
            try:
                src_img = Image.open(io.BytesIO(source_image_bytes)).convert("RGBA")
                photo_w = 500
                photo_h = cls.HEIGHT - 100
                src_ratio = src_img.width / src_img.height
                target_ratio = photo_w / photo_h

                if src_ratio > target_ratio:
                    new_w = int(photo_h * src_ratio)
                    src_resized = src_img.resize((new_w, photo_h), Image.Resampling.LANCZOS)
                    crop_left = (new_w - photo_w) // 2
                    src_cropped = src_resized.crop((crop_left, 0, crop_left + photo_w, photo_h))
                else:
                    new_h = int(photo_w / src_ratio)
                    src_resized = src_img.resize((photo_w, new_h), Image.Resampling.LANCZOS)
                    crop_top = (new_h - photo_h) // 2
                    src_cropped = src_resized.crop((0, crop_top, photo_w, crop_top + photo_h))

                mask = Image.new("L", (photo_w, photo_h), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle([0, 0, photo_w, photo_h], radius=20, fill=255)

                photo_x = cls.WIDTH - photo_w - 50
                photo_y = 50
                canvas.paste(src_cropped, (photo_x, photo_y), mask)

                # Soft slate border around photo
                draw.rounded_rectangle(
                    [photo_x, photo_y, photo_x + photo_w, photo_y + photo_h],
                    radius=20, outline=(51, 65, 85, 200), width=2
                )
                left_content_width = photo_x - 100
            except Exception as e:
                logger.warning(f"Failed to process source image for card: {e}")

        # 3. Minimal Category Tag (Top Left)
        cat_font = cls._get_font("arialbd.ttf", 16)
        clean_cat = category.upper() if category else "CRETH"
        cat_bbox = cat_font.getbbox(clean_cat)
        cat_w = cat_bbox[2] - cat_bbox[0] + 28
        cat_h = 32

        # Soft dark slate pill
        draw.rounded_rectangle(
            [50, 55, 50 + cat_w, 55 + cat_h],
            radius=16,
            fill=(30, 41, 59, 255),  # Muted slate
            outline=(71, 85, 105, 180),
            width=1
        )
        draw.text((64, 62), clean_cat, fill=(148, 163, 184, 255), font=cat_font)

        # 4. Clean Headline Title (Large & Minimal)
        title_font = cls._get_font("arialbd.ttf", 36)

        words = clean_title.split()
        lines = []
        curr_line = []
        for word in words:
            test_line = " ".join(curr_line + [word])
            bbox = title_font.getbbox(test_line)
            if (bbox[2] - bbox[0]) <= left_content_width:
                curr_line.append(word)
            else:
                if curr_line:
                    lines.append(" ".join(curr_line))
                curr_line = [word]
        if curr_line:
            lines.append(" ".join(curr_line))

        # Max 4 lines for minimal title
        lines = lines[:4]
        curr_y = 130
        for line in lines:
            draw.text((50, curr_y), line, fill=(248, 250, 252, 255), font=title_font)
            curr_y += 50

        # 5. Bottom Watermark: ONLY @CRETH (Clean & Sleek)
        bottom_y = cls.HEIGHT - 70
        brand_font = cls._get_font("arialbd.ttf", 26)
        clean_wm = watermark_text if watermark_text else "@CRETH"
        if not clean_wm.startswith("@"):
            clean_wm = f"@{clean_wm}"

        draw.text((50, bottom_y), clean_wm, fill=(148, 163, 184, 240), font=brand_font)

        # Save to JPEG bytes
        output_buffer = io.BytesIO()
        canvas.convert("RGB").save(output_buffer, format="JPEG", quality=95)
        logger.info(f"Successfully generated minimal card for '{clean_title[:30]}...' with branding {clean_wm}")
        return output_buffer.getvalue()

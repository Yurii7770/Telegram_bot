import io
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("WatermarkProcessor")

def apply_watermark(image_bytes: bytes, watermark_text: str = "@CRETH") -> bytes:
    """
    Applies a sleek semi-transparent brand watermark pill to the bottom-right corner of an image.
    Returns modified image bytes (JPEG format). If processing fails, returns original bytes.
    """
    if not image_bytes or not watermark_text:
        return image_bytes

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        width, height = image.size

        # Create overlay layer for semi-transparent drawing
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Calculate font size relative to image height
        font_size = max(16, int(height * 0.035))
        try:
            # Try loading default truetype font if available, fallback to load_default()
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # Text bounding box
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Padding around text
        pad_x = int(font_size * 0.6)
        pad_y = int(font_size * 0.4)

        pill_w = text_w + (pad_x * 2)
        pill_h = text_h + (pad_y * 2)

        # Position in bottom-right corner with margin
        margin = max(10, int(height * 0.03))
        x2 = width - margin
        y2 = height - margin
        x1 = x2 - pill_w
        y1 = y2 - pill_h

        # Draw dark translucent rounded rectangle (pill background)
        pill_radius = int(pill_h / 2)
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=pill_radius,
            fill=(15, 23, 42, 180),  # Dark navy slate, 70% opacity
            outline=(255, 255, 255, 100), # Subtle white border
            width=1
        )

        # Draw white text centered in pill
        text_x = x1 + pad_x
        text_y = y1 + pad_y - 2
        draw.text((text_x, text_y), watermark_text, fill=(255, 255, 255, 240), font=font)

        # Composite overlay with original image
        watermarked = Image.alpha_composite(image, overlay).convert("RGB")

        # Save to JPEG bytes
        output_buffer = io.BytesIO()
        watermarked.save(output_buffer, format="JPEG", quality=92)
        logger.info(f"Successfully applied watermark '{watermark_text}' to image ({width}x{height})")
        return output_buffer.getvalue()

    except Exception as e:
        logger.warning(f"Failed to apply watermark: {e}. Returning original image bytes.")
        return image_bytes

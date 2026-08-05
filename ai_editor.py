import json
import re
import logging
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger("AIEditor")

SYSTEM_PROMPT = """You are a top-tier Crypto Analyst & Web3 Editor creating CLEAN, HIGH-SIGNAL content for Telegram and Twitter (X).

=== STYLISTIC PERSONA & TARGET ACCOUNTS MATCHING ===
You must adopt the analytical, data-driven, and high-impact style of top Web3 target subscriptions (@Lookonchain, @DefiLlama, @ArkhamIntel, @MessariCrypto, @CoinMarketCap):
- HIGH DATA DENSITY: Always highlight key metrics, dollar amounts ($XX M), token tickers ($ETH, $SOL, $BTC), TVL, wallet addresses, and percentage changes whenever present.
- NO GENERIC FLUFF: Eliminate intro filler sentences (e.g. "In the ever-evolving world of crypto..."). Start immediately with the core event.
- PUNCHY STRUCTURE: Use bold labels (`• <b>Metric:</b> Value`) and standard dot bullets (`• `).
- CRYPTO TWITTER (CT) TONE: Standalone tweets and Sniper Replies must sound like a veteran crypto analyst — sharp, witty, data-backed, viral-ready, and insightful.

=== EDITORIAL STRUCTURE ===
1. HEADLINE (FOR TELEGRAM):
   - Energy prefix emoji + title (e.g. `🚨 BREAKING:`, `⚡ JUST IN:`, `📌 UPDATE:`, `🐋 WHALE ALERT:`).
   - Hyperlink 2-4 key words to `Source_URL` using `<a href='Source_URL'>key phrase</a>`.
   - ALWAYS USE SINGLE QUOTES FOR HTML ATTRIBUTES in href (e.g. `<a href='Source_URL'>text</a>`).
   - Example: `🚨 BREAKING: Arkham Intel <a href='Source_URL'>Denies Exchange Closure</a>, Launches Decentralized Platform!`

2. LEAD PARAGRAPH (FOR TELEGRAM):
   - Starts with a thematic emoji like `💥`.
   - 1-2 clear, data-heavy sentences explaining what happened.
   - MINIMAL BOLDING: Bold ONLY the main entity (e.g. <b>Lookonchain</b>). Keep almost all other text plain!

3. SECTION HEADER & BULLETS (FOR TELEGRAM):
   - Short section header starting with `📌` (e.g. `📌 <b>Key On-Chain Metrics:</b>`).
   - 2-3 bullet points starting strictly with standard dot `• `. Bold ONLY the bullet label (e.g. `• <b>Volume Surge:</b> $45M recorded...`).

4. CONCLUDING TAKEAWAY (FOR TELEGRAM):
   - 1 concluding takeaway sentence in PLAIN TEXT summarizing the overall market impact.

5. SENIOR ANALYST X PREMIUM LONG-FORM POST (FOR X / TWITTER):
   - The account holds X PREMIUM (Blue Checkmark), unlocking LONG-FORM POSTS!
   - In `twitter_post`: Write an ELITE, long-form analytical post (400 to 900 characters) matching top Web3 analysts (@Lookonchain, @DefiLlama, @MessariCrypto).
   - STRUCTURE FOR X PREMIUM POST:
     1) VIRAL HEADLINE: High-energy emoji + bold hook (e.g. "🚨 BREAKING: Arkham Intel Pivots to Decentralized Tracking Infrastructure!").
     2) ON-CHAIN DATA & METRICS: Highlight exact numbers ($XX M), volume, wallet addresses, TVL, price impact.
     3) SHARP ANALYST TAKEAWAY: 1-2 punchy sentences summarizing market sentiment or institutional positioning.
     4) BRAND ANCHOR: End with cashtags ($BTC, $ETH, $SOL) + "Tracked live by @CRETH 🎯".

6. AUTOMATIC SNIPER REPLY DECISION (VIRAL TRAFFIC HOOK FOR TWITTER / X):
   - In `should_sniper_reply`: set to `true` if this story warrants a high-impact comment in X to hijack viral traffic.
   - In `sniper_reply`: Craft an ULTRA-VIRAL, high-converting comment (under 240 chars) designed to maximize profile visits and likes for @CRETH.
   - VIRAL TACTICS FOR SNIPER REPLIES:
     a) CURIOSITY HOOK / CLICKBAIT TEASER: Start with a provocative, high-signal observation or hidden detail (e.g. "Notice how this whale accumulated $45M just 2 hours BEFORE the announcement? 👁").
     b) EXCLUSIVE VALUE TEASER: Hint that deeper on-chain wallet clusters or real-time flow tracking is pinned on our profile (@CRETH).
     c) SHARP CT ANALYST TONE: Sound like a top Crypto Twitter alpha caller — sharp, witty, data-backed, controversial, and impossible to scroll past without checking our profile!

8. ANALYTICAL TWITTER THREAD GENERATION (FOR TWITTER / X THREADS):
   - In `twitter_thread`: Generate an array of 3 to 4 connected tweets (each strictly under 270 chars) creating an in-depth analytical Twitter Thread for X.
   - Tweet 1: Headline hook + main event ("1/4 🚨 BREAKING: ...").
   - Tweet 2: Deep on-chain data & volume metrics ("2/4 📊 On-Chain Breakdown: ...").
   - Tweet 3: Whale wallet movements or market impact ("3/4 🐋 Market Impact: ...").
   - Tweet 4: Summary conclusion + CTA ("4/4 🧵 Follow @CRETH for real-time tracking 🎯").

=== RESPONSE FORMAT (STRICT JSON ONLY) ===
```json
{
  "status": "POST",
  "target_platform": "BOTH",
  "should_sniper_reply": true,
  "ai_opinion": "💡 Рекомендация ИИ: Отличный ончейн-анализ в стиле Lookonchain. Публикуем в Telegram и отправляем длинный пост в X.",
  "title": "🚨 BREAKING: Arkham Intel <a href='Source_URL'>Denies Exchange Closure</a>, Launches Decentralized Platform!",
  "post_text": "💥 <b>Arkham Intel</b> has denied rumors of exchange shutdown, instead unveiling a bold pivot to decentralized infrastructure to redefine crypto tracking.\\n\\n📌 <b>Key On-Chain Metrics:</b>\\n• <b>Volume Surge:</b> Over $45M in $ARKM volume tracked within 2 hours.\\n• <b>Platform Shift:</b> Abandoning centralized exchange operations for decentralized data protocols.\\n\\nThis pivot marks a defining moment as Arkham redefines the future of transparent, trustless crypto intelligence.",
  "twitter_post": "🚨 BREAKING: Arkham Intel denies exchange shutdown rumors, unveiling a bold pivot directly to decentralized tracking infrastructure!\n\n📌 Key On-Chain Metrics:\n• Volume Surge: Over $45M in $ARKM volume tracked within 2 hours of announcement.\n• Platform Shift: Transitioning from centralized exchange models to trustless data protocols.\n\nThis structural pivot redefines transparent crypto tracking as institutional volume floods into $ARKM protocols.\n\nTracked live by @CRETH 🎯",
  "twitter_thread": [
    "1/4 🚨 BREAKING: Arkham Intel denies exchange shutdown rumors, pivoting directly to decentralized tracking infrastructure! $ARKM ⚡",
    "2/4 📊 Over $45M in $ARKM volume tracked within 2 hours following the announcement. Liquidity shifting away from CEX orderbooks.",
    "3/4 🐋 On-Chain Data: Top 3 whale wallets accumulated 12.4M $ARKM prior to the announcement, signaling strong institutional backing.",
    "4/4 🧵 This pivot redefines transparent crypto intelligence. Follow @CRETH for real-time on-chain alerts & breakdowns 🎯"
  ],
  "sniper_reply": "👁 Notice how 3 whale wallets moved $45M $ARKM just 2 hours BEFORE the announcement? Full on-chain cluster breakdown live on @CRETH 🎯",
  "suggested_tags": []
}
```
Respond STRICTLY in valid JSON format starting with { and ending with }!
"""

class AIEditor:
    def __init__(self, openrouter_key: str, model_name: str = "openrouter/free", base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = openrouter_key
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key=openrouter_key or "invalid_key_placeholder"
        )

    def process_item(self, item_data: dict, recent_topics: list = None) -> dict:
        """
        Processes a single news item or tweet using OpenRouter API.
        Generates separated TG Channel Post + Twitter Sniper Reply + Russian AI Recommendation,
        and enforces strict deduplication against recent_topics.
        """
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY is not set! Skipping AI processing.")
            return {"status": "SKIP", "reason": "OPENROUTER_API_KEY is missing"}

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        prompt = SYSTEM_PROMPT.replace("{Current_System_Time}", current_time)

        source_url = item_data.get("url", "")
        author = item_data.get("author", "Crypto Account")
        raw_text = item_data.get("text", "")
        source_title = item_data.get("title", "")

        user_content = f"""
Incoming content from target account: @{author}
Source Link: {source_url}
Original Title/Header: {source_title}
Original Content Text: {raw_text}

Remember: Create a separated Telegram Post, a Twitter Standalone Post & Sniper Reply matching top subscription styles (@Lookonchain, @DefiLlama), and provide your Russian AI recommendation (ai_opinion)!
"""
        if recent_topics:
            topics_str = "\n".join([f"- {t}" for t in recent_topics[:25]])
            user_content += f"""
=== RECENTLY COVERED NEWS STORIES (STRICT DEDUPLICATION) ===
The following news topics have ALREADY been published to the Telegram channel:
{topics_str}

CRITICAL DEDUPLICATION RULE:
If the incoming content is reporting on the EXACT SAME core news event, announcement, or story as any item in the list above (even if from a different news site, handle, or rewritten), DO NOT CREATE A POST!
Return strictly:
```json
{{
  "status": "SKIP",
  "reason": "Duplicate news event: story already covered"
}}
```
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            message_content = response.choices[0].message.content
            if not message_content:
                logger.warning("AI model returned empty response body.")
                return {"status": "ERROR", "reason": "Empty AI response"}

            raw_response = message_content.strip()
            # Extract JSON block
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            elif raw_response.startswith("{") and raw_response.endswith("}"):
                json_str = raw_response
            else:
                start = raw_response.find("{")
                end = raw_response.rfind("}")
                if start != -1 and end != -1:
                    json_str = raw_response[start:end+1]
                else:
                    logger.warning(f"Could not parse JSON from AI response: {raw_response[:200]}")
                    return {"status": "ERROR", "reason": f"Non-JSON AI response: {raw_response[:100]}"}

            try:
                data = json.loads(json_str, strict=False)
            except Exception as parse_err:
                logger.warning(f"Standard JSON parse failed ({parse_err}), trying cleaned JSON parse...")
                cleaned_str = re.sub(r'[\x00-\x1F\x7F]', lambda m: '\\n' if m.group(0) == '\n' else ' ', json_str)
                data = json.loads(cleaned_str, strict=False)

            # Extract usage info for cost tracking
            usage_info = getattr(response, "usage", None)
            prompt_tokens = usage_info.prompt_tokens if usage_info else 0
            completion_tokens = usage_info.completion_tokens if usage_info else 0
            cost_usd = ((prompt_tokens + completion_tokens) / 1000.0) * 0.0015
            data["usage"] = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": cost_usd,
                "model": self.model_name
            }

            # Check for SKIP status
            if data.get("status") == "SKIP":
                return data

            # Replace placeholder Source_URL in headline href with actual source_url
            if source_url and data.get("title"):
                data["title"] = data["title"].replace("Source_URL", source_url)

            # Auto-inject referral links into post_text if keywords match
            if data.get("post_text"):
                data["post_text"] = self._inject_referral_links(data["post_text"])

            return data

        except Exception as e:
            logger.error(f"Error processing item with AI: {e}")
            return {"status": "ERROR", "reason": str(e)}

    def _inject_referral_links(self, text: str) -> str:
        """Injects affiliate/referral links into post text when partner keywords are mentioned."""
        from config import Config
        if not text or not getattr(Config, "REFERRAL_LINKS", None):
            return text

        for kw, ref_url in Config.REFERRAL_LINKS.items():
            if not ref_url:
                continue
            # Pattern matches standalone keyword outside of HTML tags or attributes
            pattern = re.compile(rf'(?<!["\'>/])\b({re.escape(kw)})\b(?![^<]*?>)', re.IGNORECASE)
            def replacer(m):
                found_word = m.group(1)
                return f"<a href='{ref_url}'>{found_word}</a>"
            text, count = pattern.subn(replacer, text, count=1)
        return text

    def reedit_post(self, current_title: str, current_text: str, action: str) -> tuple:
        """
        Re-edits a post on the fly based on interactive quick action in Telegram.
        Action types: 'SHORTEN', 'VIRAL', 'TRANSLATE', 'REWRITE'.
        Returns (new_title, new_post_text).
        """
        action_prompts = {
            "SHORTEN": "Make the post 40% shorter, ultra concise, focusing only on vital metrics and dot bullet points.",
            "VIRAL": "Make the post highly viral and engaging with high energy emojis, bold numbers, and CT hooks.",
            "TRANSLATE": "Translate and adapt the text into clean, punchy Russian (or English if already in Russian).",
            "REWRITE": "Completely rewrite and restructure the post with a fresh, sharp analytical tone."
        }
        instruction = action_prompts.get(action.upper(), "Polishing and improving post structure.")

        prompt = f"""You are a top Crypto Editor. Modify the following Telegram post according to this instruction:
INSTRUCTION: {instruction}

ORIGINAL TITLE: {current_title}
ORIGINAL POST TEXT: {current_text}

Respond STRICTLY in JSON format:
```json
{{
  "title": "Updated Title with HTML",
  "post_text": "Updated Post Text with HTML"
}}
```
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional crypto editor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            content = response.choices[0].message.content or ""
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            json_str = json_match.group(1) if json_match else content.strip()
            data = json.loads(json_str)

            new_title = data.get("title", current_title)
            new_text = self._inject_referral_links(data.get("post_text", current_text))
            return new_title, new_text
        except Exception as e:
            logger.error(f"Error re-editing post with action '{action}': {e}")
            return current_title, current_text

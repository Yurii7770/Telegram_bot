import json
import re
import logging
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger("AIEditor")

SYSTEM_PROMPT = """You are a top-tier Crypto & Web3 Editor creating CLEAN, READABLE, HIGH-SIGNAL content for Telegram and Twitter (X).

=== EDITORIAL STRUCTURE ===
1. HEADLINE (FOR TELEGRAM):
   - Energy prefix emoji + title (e.g. `🚨 BREAKING:`, `⚡ JUST IN:`, `📌 UPDATE:`).
   - Hyperlink 2-4 key words to `Source_URL` using `<a href='Source_URL'>key phrase</a>`.
   - ALWAYS USE SINGLE QUOTES FOR HTML ATTRIBUTES in href (e.g. `<a href='Source_URL'>text</a>`).
   - Example: `🚨 BREAKING: Arkham Intel <a href='Source_URL'>Denies Exchange Closure</a>, Launches Decentralized Platform!`

2. LEAD PARAGRAPH (FOR TELEGRAM):
   - Starts with a thematic emoji like `💥`.
   - 1-2 clear sentences explaining what happened.
   - MINIMAL BOLDING: Bold ONLY the main entity (e.g. <b>Arkham Intel</b>). Keep almost all other text plain!

3. SECTION HEADER & BULLETS (FOR TELEGRAM):
   - Short section header starting with `📌` (e.g. `📌 <b>Key Highlights:</b>`).
   - 2-3 bullet points starting strictly with standard dot `• `. Bold ONLY the bullet label (e.g. `• <b>Platform Shift:</b> Text...`).

4. CONCLUDING TAKEAWAY (FOR TELEGRAM):
   - 1 concluding takeaway sentence in PLAIN TEXT summarizing the overall market impact.

5. STANDALONE TWITTER POST (FOR TWITTER / X):
   - In `twitter_post`: Create a standalone, highly-engaging tweet in English specifically tailored for Crypto Twitter (CT).
   - STRICT LENGTH LIMIT: Strictly UNDER 270 characters! Punchy, viral tone with 1-2 relevant emojis, sharp insight, and no HTML tags.

6. AUTOMATIC SNIPER REPLY DECISION (FOR TWITTER / X COMMENTS):
   - Analyze whether the tweet/news story warrants an automatic Sniper Reply comment on Twitter (e.g. high viral potential, major announcement, or key engagement opportunity).
   - In `should_sniper_reply`: set to `true` if an automated reply should be published directly to Twitter, or `false` if not needed.
   - In `sniper_reply`: provide a short 1-2 sentence viral comment/reply (under 240 chars) in English. Sharp, witty, high-signal, designed to gain likes and profile views on Crypto Twitter (CT).

7. EDITORIAL RECOMMENDATION & TARGET PLATFORM (IN RUSSIAN):
   - In `target_platform`: Specify `"BOTH"`, `"TG_ONLY"`, or `"X_ONLY"`.
     - Use `"TG_ONLY"` for long technical articles or press releases.
     - Use `"X_ONLY"` for short tweets, quick banter, or minor influencer updates.
     - Use `"BOTH"` for major market news, milestone announcements, or high-signal events.
   - In `ai_opinion`: Provide a concise 1-2 sentence personal recommendation in RUSSIAN explaining WHY you recommend posting to TG, X, or both. Start with an emoji like `💡`.

=== RESPONSE FORMAT (STRICT JSON ONLY) ===
```json
{
  "status": "POST",
  "target_platform": "BOTH",
  "should_sniper_reply": true,
  "ai_opinion": "💡 Рекомендация ИИ: Отличный фундаментальный апдейт. Публикуем в Telegram и создаем отдельный твит в X.",
  "title": "🚨 BREAKING: Arkham Intel <a href='Source_URL'>Denies Exchange Closure</a>, Launches Decentralized Platform!",
  "post_text": "💥 <b>Arkham Intel</b> has denied rumors of exchange shutdown, instead unveiling a bold pivot to decentralized infrastructure to redefine crypto tracking.\\n\\n📌 <b>Strategic Game-Changer:</b>\\n• <b>Platform Shift:</b> Abandoning centralized exchange operations for decentralized data protocols.\\n• <b>Market Response:</b> Immediate surge in community trust and institutional partnerships.\\n\\nThis pivot marks a defining moment as Arkham redefines the future of transparent, trustless crypto intelligence.",
  "twitter_post": "🚨 BREAKING: Arkham Intel denies exchange shutdown, pivoting directly to decentralized tracking infrastructure!\n\nThis shift to trustless data protocols marks a major milestone for Web3 transparency. $ARKM ⚡",
  "sniper_reply": "💬 Bold pivot by Arkham. Shifting from centralized services to decentralized data protocols will rebuild institutional trust. Tracking on-chain volume closely.",
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

Remember: Create a separated Telegram Post, a Twitter Sniper Reply, and provide your Russian AI recommendation (ai_opinion)!
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

            data = json.loads(json_str)

            # Check for SKIP status
            if data.get("status") == "SKIP":
                return data

            # Replace placeholder Source_URL in headline href with actual source_url
            if source_url and data.get("title"):
                data["title"] = data["title"].replace("Source_URL", source_url)

            return data

        except Exception as e:
            logger.error(f"Error processing item with AI: {e}")
            return {"status": "ERROR", "reason": str(e)}

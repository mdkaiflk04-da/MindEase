"""
chatbot.py - Sentiment analysis and crisis detection only.
All response generation is handled by Gemini API in app.py.
"""

from textblob import TextBlob

# ─────────────────────────────────────────────
#  CRISIS KEYWORDS
# ─────────────────────────────────────────────
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "die", "hopeless", "no reason to live", "can't go on", "self harm",
    "hurt myself", "not worth living", "end it all"
]

# ─────────────────────────────────────────────
#  SENTIMENT ANALYSIS
# ─────────────────────────────────────────────
def analyze_sentiment(text: str) -> str:
    """Return sentiment label for a single message."""
    lower = text.lower()
    if any(kw in lower for kw in CRISIS_KEYWORDS):
        return "crisis"
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    return "neutral"


def analyze_conversation_sentiment(history: list) -> str:
    """
    Analyze sentiment across the ENTIRE conversation history.
    history: list of {"role": "user"|"model", "parts": [{"text": str}]}
    Returns overall sentiment label.
    """
    user_messages = []
    for m in history:
        if m.get("role") == "user":
            for part in m.get("parts", []):
                if "text" in part:
                    user_messages.append(part["text"])

    if not user_messages:
        return "neutral"

    combined = " ".join(user_messages)
    lower = combined.lower()

    crisis_count = sum(1 for kw in CRISIS_KEYWORDS if kw in lower)
    if crisis_count >= 1:
        return "crisis"

    blob = TextBlob(combined)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    return "neutral"

"""
chatbot.py - Core chatbot logic: response generation, sentiment analysis, memory
"""

import random
from textblob import TextBlob
import datetime

# ─────────────────────────────────────────────
#  CRISIS KEYWORDS
# ─────────────────────────────────────────────
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "die", "hopeless", "no reason to live", "can't go on", "self harm",
    "hurt myself", "not worth living"
]

# ─────────────────────────────────────────────
#  KEYWORD → RESPONSE BANK
# ─────────────────────────────────────────────
KEYWORD_RESPONSES = {
    "stress": [
        "Stress can feel overwhelming. 🌿 Have you tried taking a few slow, deep breaths?",
        "Stress is your mind asking for a break. What's weighing on you most right now?",
        "I hear you — stress is exhausting. Would it help to talk through what's causing it? 💛",
    ],
    "lonely": [
        "Loneliness is one of the hardest feelings. 🤗 You're not alone right now — I'm here.",
        "Feeling lonely doesn't mean you're alone. Want to tell me more about what's going on?",
        "I'm really glad you shared that. Loneliness can feel so heavy. 💙 What would make today a little easier?",
    ],
    "tired": [
        "Being tired — especially emotionally — is real and valid. 😴 Rest is not weakness.",
        "When did you last do something just for yourself? Even five quiet minutes can help. 🌙",
        "Your body and mind are telling you something important. Are you getting enough rest? 💤",
    ],
    "anxiety": [
        "Anxiety can be so consuming. 🌊 Try grounding yourself: name 5 things you can see right now.",
        "I understand — anxiety can make everything feel urgent and scary. Take it one breath at a time. 🫁",
        "You're not your anxiety. What usually helps you feel a little calmer? 🍃",
    ],
    "sad": [
        "It's okay to feel sad. 🌧️ Your feelings are valid. Do you want to talk about what happened?",
        "Sadness is part of being human. I'm here to listen without judgment. 💜",
        "I'm sorry you're feeling down. Would sharing what's on your mind help lighten the load?",
    ],
    "angry": [
        "Anger often hides something deeper — hurt, fear, or frustration. 🔥 What triggered this?",
        "It's okay to feel angry. What happened that made you feel this way? 😤",
        "Your anger is valid. Let's talk through it — sometimes just naming the cause helps. 💬",
    ],
    "happy": [
        "That's wonderful to hear! 😊 What's bringing you joy today?",
        "Your happiness is contagious! Tell me more — good news deserves celebrating! 🎉",
        "Love that energy! ✨ What happened?",
    ],
    "help": [
        "Of course — I'm here for you. What kind of support do you need right now? 🤝",
        "You reached out, and that takes courage. 💛 What's going on?",
        "Tell me what's happening. I'm listening and I care. 🌟",
    ],
}

# ─────────────────────────────────────────────
#  GENERIC FALLBACK RESPONSES (no repetition pool)
# ─────────────────────────────────────────────
GENERIC_RESPONSES = [
    "I'm here and I'm listening. 💙 Can you tell me more about how you're feeling?",
    "Thank you for sharing that with me. What's been on your mind lately?",
    "That sounds important. How long have you been feeling this way?",
    "I hear you. Would you like to explore what's behind those feelings?",
    "You're not alone in this. 🌿 What do you think would help most right now?",
    "Sometimes putting feelings into words is the first step. Keep going — I'm here. ✨",
    "Every feeling you have makes sense given your experience. What would you like to focus on?",
    "I'm here, no judgment. 💛 What would feel most helpful right now?",
    "It takes strength to talk about these things. What else is on your heart?",
    "I appreciate you trusting me with this. 🌸 How can I best support you today?",
]

# ─────────────────────────────────────────────
#  EMOJI SENTIMENT MAP
# ─────────────────────────────────────────────
EMOJI_SENTIMENT = {
    "😊": ("positive", "I see that smile! 😊 What's making you happy today?"),
    "😢": ("negative", "I see that tear. 😢 It's okay to feel sad — I'm here for you."),
    "😡": ("negative", "I sense some frustration. 😡 Want to talk about what's bothering you?"),
    "❤️": ("positive", "Sending love right back! ❤️ How are you feeling today?"),
}

# ─────────────────────────────────────────────
#  MEMORY CLASS
# ─────────────────────────────────────────────
class Memory:
    """Stores conversation history and user profile, limited to last N messages."""

    MAX_HISTORY = 20

    def __init__(self):
        self.history = []        # list of {"role": "user"|"bot", "text": str}
        self.user_name = None
        self.last_bot_responses = []   # track recent bot replies to avoid repetition

    def add(self, role: str, text: str):
        self.history.append({"role": role, "text": text, "time": datetime.datetime.now().isoformat()})
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)

    def extract_name(self, text: str):
        """Try to detect 'my name is X' patterns."""
        lower = text.lower()
        for phrase in ["my name is ", "i am ", "i'm ", "call me "]:
            if phrase in lower:
                idx = lower.index(phrase) + len(phrase)
                name_candidate = text[idx:].split()[0].strip(".,!?")
                if name_candidate.isalpha():
                    self.user_name = name_candidate.capitalize()
                    return True
        return False

    def greeting(self) -> str:
        return f"{self.user_name}" if self.user_name else "friend"

    def recent_user_messages(self, n=3) -> list:
        return [m["text"] for m in self.history if m["role"] == "user"][-n:]

    def is_repeated_message(self, text: str) -> bool:
        recent = self.recent_user_messages(5)
        return recent.count(text.lower()) >= 2

    def unique_bot_response(self, candidates: list) -> str:
        """Pick a response not recently used."""
        unused = [r for r in candidates if r not in self.last_bot_responses]
        pool = unused if unused else candidates
        choice = random.choice(pool)
        self.last_bot_responses.append(choice)
        if len(self.last_bot_responses) > 6:
            self.last_bot_responses.pop(0)
        return choice


# ─────────────────────────────────────────────
#  SENTIMENT ANALYSIS
# ─────────────────────────────────────────────
def analyze_sentiment(text: str) -> str:
    """Return sentiment label: crisis / positive / negative / neutral."""
    lower = text.lower()

    # Crisis check first (highest priority)
    if any(kw in lower for kw in CRISIS_KEYWORDS):
        return "crisis"

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"


# ─────────────────────────────────────────────
#  RESPONSE GENERATOR
# ─────────────────────────────────────────────
def generate_response(message: str, memory: Memory) -> str:
    """Generate a context-aware, empathetic response."""

    lower = message.lower().strip()

    # 1. Store message in memory + extract name
    memory.add("user", lower)
    memory.extract_name(message)

    # 2. Detect repeated message
    if memory.is_repeated_message(lower):
        return (f"You've mentioned that a few times, {memory.greeting()}. "
                "It seems really important to you. 💙 Let's talk about it more deeply — what's at the core of this feeling?")

    # 3. Crisis response
    sentiment = analyze_sentiment(message)
    if sentiment == "crisis":
        return (
            f"I'm really concerned about you right now, {memory.greeting()}. 💙 "
            "What you're feeling is real, but please know that help is available. "
            "Please reach out to someone you trust, or contact a crisis helpline immediately. "
            "You matter deeply — this pain can get better with support. 🌟 "
            "iCall India: 9152987821 | Vandrevala Foundation: 1860-2662-345"
        )

    # 4. Emoji-only message
    for emoji, (_, reply) in EMOJI_SENTIMENT.items():
        if message.strip() == emoji:
            memory.add("bot", reply)
            return reply

    # 5. Greeting detection
    if any(g in lower for g in ["hello", "hi", "hey", "good morning", "good evening"]):
        name_part = f", {memory.user_name}" if memory.user_name else ""
        response = random.choice([
            f"Hello{name_part}! 😊 I'm so glad you're here. How are you feeling today?",
            f"Hey{name_part}! 🌟 Welcome. What's on your mind?",
            f"Hi{name_part}! 💙 This is a safe space. How can I support you today?",
        ])
        memory.add("bot", response)
        return response

    # 6. Name introduction response
    if memory.extract_name(message):
        response = f"It's lovely to meet you, {memory.user_name}! 🌸 How are you feeling today?"
        memory.add("bot", response)
        return response

    # 7. Keyword-based response
    for keyword, responses in KEYWORD_RESPONSES.items():
        if keyword in lower:
            response = memory.unique_bot_response(responses)
            # Add contextual follow-up if there's prior history
            if len(memory.history) > 4:
                response += f" Earlier you mentioned something too, {memory.greeting()} — I want to make sure I understand the full picture."
            memory.add("bot", response)
            return response

    # 8. Sentiment-based generic response
    if sentiment == "positive":
        candidates = [
            f"That's so good to hear, {memory.greeting()}! 🎉 Tell me more!",
            f"Love the positive energy! ✨ What's going well for you?",
            f"You sound uplifted! 😊 What's contributing to that feeling?",
        ]
    elif sentiment == "negative":
        candidates = [
            f"I'm sorry you're going through this, {memory.greeting()}. 💙 Want to share more?",
            f"That sounds really tough. I'm here to listen without any judgment. 💜",
            f"Difficult feelings are valid. 🌿 What would help you most right now?",
        ]
    else:
        candidates = GENERIC_RESPONSES

    response = memory.unique_bot_response(candidates)
    memory.add("bot", response)
    return response

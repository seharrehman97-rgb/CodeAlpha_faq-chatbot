"""Small-talk intents: simple pattern matching for greetings, thanks, "who are you", etc.

Each pattern must match the WHOLE message (not just a word inside it), so a real
question such as "hi, my webhook is not firing" is never treated as small talk.
"""
import re

TOPICS = (
    "HTTP status codes, API basics, authentication, headers, CORS, "
    "rate limiting, webhooks, and debugging tools"
)
EXAMPLES = "Try: 'What does a 401 mean?' or 'Why is my webhook not firing?'"

INTENTS = [
    (
        r"(hi|hello|hey|good (morning|afternoon|evening))( there| bot)?",
        f"Hi! I can answer questions about {TOPICS}. {EXAMPLES}",
    ),
    (
        r"(thanks|thank you|thx)( a lot| so much)?",
        "You're welcome! Ask me another API or webhook question any time.",
    ),
    (
        r"(bye|goodbye|see you|see you later)",
        "Goodbye! Good luck with your API debugging.",
    ),
    (
        r"(who are you|what are you|what('?s| is) your name|what your name|your name)",
        "I'm the REST API & Webhook Troubleshooter, an FAQ chatbot for developers. "
        f"I cover {TOPICS}.",
    ),
    (
        r"(help|help me|what can you do|what do you do|how can you help( me)?)",
        f"I can answer questions about {TOPICS}. {EXAMPLES}",
    ),
    (
        r"(tell|say)( me)?( a)? jokes?",
        f"I'm not much of a comedian, but I can help you debug an API. {EXAMPLES}",
    ),
]


def small_talk_reply(text: str):
    """Return a canned reply if the whole message is small talk, otherwise None."""
    cleaned = re.sub(r"[^a-z0-9' ]", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for pattern, reply in INTENTS:
        if re.fullmatch(pattern, cleaned):
            return reply
    return None


if __name__ == "__main__":
    tests = [
        "Hi!", "thanks", "who are you?", "what is your name", "help", "tell me a joke",
        "hi, my webhook is not firing", "help me with a 401 error", "tell a joke",
    ]
    for t in tests:
        print(f"{t!r:35} -> {small_talk_reply(t)!r}")
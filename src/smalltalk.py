"""Small-talk intents: simple pattern matching for questions ABOUT the bot.

Two kinds of patterns are used:
1. INTENTS: the pattern must match the WHOLE message ("hi", "thanks", "who are you"),
   so a real question such as "hi, my webhook is not firing" is never intercepted.
2. ABOUT_BOT: keyword patterns for longer questions about the bot itself, such as
   "how can you benefit developers?". These only apply to short messages that talk to
   the bot ("you"/"your"), contain no status code, and mention no API topic.
"""
import re

TOPICS = (
    "HTTP status codes, API basics, authentication, headers, CORS, "
    "rate limiting, webhooks, and debugging tools"
)
EXAMPLES = "Try: 'What does a 401 mean?' or 'Why is my webhook not firing?'"

CAPABILITIES = (
    "Here is how I can help developers:\n\n"
    "- **Explain HTTP status codes** (401, 404, 429, 502 and more) and what to do about them\n"
    "- **Troubleshoot authentication** problems: API keys, Bearer tokens, JWT, OAuth\n"
    "- **Explain CORS errors**, rate limits, and retry strategies\n"
    "- **Debug webhooks**: not firing, duplicate events, signatures, testing locally with ngrok\n"
    "- **Show how to test APIs** with Postman, curl, and browser DevTools\n\n"
    "Every answer comes with a link to the official documentation. " + EXAMPLES
)

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
        CAPABILITIES,
    ),
    (
        r"(tell|say)( me)?( a)? jokes?",
        f"I'm not much of a comedian, but I can help you debug an API. {EXAMPLES}",
    ),
]

# Longer questions about the bot, e.g. "which things you can do for developers,
# can you tell how you can benefit developers".
ABOUT_BOT = re.compile(
    r"\b(benefit|what can you do|what do you do|things you can do|things can you do|"
    r"what are you good for|your features|your purpose|how useful)\b"
)
TALKS_TO_BOT = re.compile(r"\b(you|your|chatbot|bot)\b")
STATUS_CODE = re.compile(r"\b[1-5]\d{2}\b")
API_TOPIC_WORDS = re.compile(
    r"\b(cors|webhooks?|tokens?|jwt|oauth|headers?|postman|curl|ngrok|rate limit|status codes?)\b"
)
MAX_WORDS = 20


def small_talk_reply(text: str):
    """Return a canned reply if the message is small talk, otherwise None."""
    cleaned = re.sub(r"[^a-z0-9' ]", " ", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    for pattern, reply in INTENTS:
        if re.fullmatch(pattern, cleaned):
            return reply

    if (
        len(cleaned.split()) <= MAX_WORDS
        and ABOUT_BOT.search(cleaned)
        and TALKS_TO_BOT.search(cleaned)
        and not STATUS_CODE.search(cleaned)
        and not API_TOPIC_WORDS.search(cleaned)
    ):
        return CAPABILITIES
    return None


if __name__ == "__main__":
    tests = [
        "which things you can do for developers, can you tell how you can benefit developers",
        "how can you benefit developers?",
        "what can you do",
        "help",
        "Hi!",
        "tell me a joke",
        "hi, my webhook is not firing",
        "help me with a 401 error",
        "what can you do about a 502",
        "how can you benefit developers working with webhooks",
        "this tool is a benefit to my team",
    ]
    for t in tests:
        reply = small_talk_reply(t)
        print(f"{t[:62]!r:66} -> {'(capabilities list)' if reply == CAPABILITIES else (reply[:40] + '...' if reply else None)!r}")
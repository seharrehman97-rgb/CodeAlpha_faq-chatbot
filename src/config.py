"""Settings used across the project. Change values here, not inside the logic."""

FAQ_PATH = "data/faqs.csv"

# If the best match scores below this, the bot admits it is not sure.
# 0.30 is a starting guess; it will be tuned with the test set in Stage 6.
THRESHOLD = 0.30

# How many "you could also ask" questions to show, and the minimum score
# a question needs to be worth suggesting.
NUM_SUGGESTIONS = 3
MIN_SUGGESTION_SCORE = 0.15

FALLBACK_MESSAGE = (
    "Sorry, I'm not sure about that. Could you rephrase it, "
    "or try one of these questions?"
)
OUT_OF_SCOPE_MESSAGE = (
    "Sorry, I don't have an answer for that. I can help with REST API and "
    "webhook problems: status codes, authentication, CORS, rate limits, "
    "webhooks, and debugging tools."
)
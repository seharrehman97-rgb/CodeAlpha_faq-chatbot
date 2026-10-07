"""Settings used across the project. Change values here, not inside the logic."""

FAQ_PATH = "data/faqs.csv"

# If the best match scores below this, the bot admits it is not sure.
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

# ---------------------------------------------------------------------------
# Tuning options (Stage 6b). The defaults below give the original baseline.
# Run `python -m src.experiments` to see which options help, then copy the
# winning values here.
# ---------------------------------------------------------------------------

# Extra words to ignore when matching, e.g. {"request", "send"}.
EXTRA_STOPWORDS = set()

# True = also match two-word phrases such as "bad gateway" or "refresh token".
USE_BIGRAMS = False

# Share of the user's words that must exist in the FAQ vocabulary (0 = off).
# Stops off-topic questions that contain only one familiar word.
MIN_COVERAGE = 0.0

# The best FAQ must beat the second-best by at least this much (0 = off).
# Stops the bot guessing when two FAQs look almost equally good.
MIN_MARGIN = 0.0

# True = refuse whenever the user types a status code that no FAQ covers.
STRICT_CODES = False
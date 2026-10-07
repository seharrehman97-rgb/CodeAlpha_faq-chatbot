"""Text preprocessing for the FAQ chatbot, using spaCy.

Pipeline: clean -> tokenize -> remove stopwords -> lemmatize.
The same functions are used for the FAQ questions AND the user's question,
so both are converted in exactly the same way.
"""
import re

import spacy

from src import config

# Load spaCy's small English model once (loading is slow, so do it only once).
# The parser and named-entity recogniser are not needed, so we switch them off.
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# spaCy treats these as stopwords, but they change the meaning of a
# troubleshooting question ("webhook NOT firing", "server DOWN"), so we keep them.
KEEP_WORDS = {"not", "no", "never", "without", "down"}
STOP_WORDS = nlp.Defaults.stop_words - KEEP_WORDS

# Words whose lemma spaCy gets wrong (it treats "cors" as a plural and shortens it
# to "cor"), so we keep them exactly as written.
KEEP_AS_IS = {"cors", "https"}


def clean_text(text: str) -> str:
    """Step 1 - Clean: lowercase and replace punctuation/special characters with spaces."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)  # keep only letters, digits, spaces
    text = re.sub(r"\s+", " ", text).strip()  # collapse repeated spaces
    return text


def _keep(token) -> bool:
    """Step 3 - Stopword removal: decide whether a token is worth keeping."""
    if token.is_space:
        return False
    # config.EXTRA_STOPWORDS is read here, so experiments can change it on the fly.
    words_to_drop = STOP_WORDS | config.EXTRA_STOPWORDS
    return token.text not in words_to_drop and token.lemma_ not in words_to_drop


def _normalize(token) -> str:
    """Step 4 - Lemmatize: reduce a token to its base form (unless it is protected)."""
    return token.text if token.text in KEEP_AS_IS else token.lemma_


def preprocess(text: str) -> str:
    """Run the full pipeline on ONE text and return the tokens joined by spaces."""
    doc = nlp(clean_text(text))  # Step 2 - Tokenize (spaCy splits the text into tokens)
    tokens = [_normalize(t) for t in doc if _keep(t)]
    return " ".join(tokens)


def preprocess_many(texts) -> list[str]:
    """Same as preprocess(), but faster for many texts (e.g. all FAQ questions)."""
    cleaned = [clean_text(t) for t in texts]
    return [" ".join(_normalize(t) for t in doc if _keep(t)) for doc in nlp.pipe(cleaned)]


if __name__ == "__main__":
    examples = [
        "Why am I getting a 401 error?",
        "My webhook is NOT firing!!",
        "CORS policy: No 'Access-Control-Allow-Origin' header is present",
        "What does 429 Too Many Requests mean?",
    ]
    for e in examples:
        print(f"{e!r}\n   -> {preprocess(e)!r}\n")
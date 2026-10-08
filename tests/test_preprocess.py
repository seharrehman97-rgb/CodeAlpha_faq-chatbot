"""Tests for the spaCy preprocessing steps."""
from src.preprocess import clean_text, preprocess


def test_clean_text_lowercases_and_removes_punctuation():
    assert clean_text("Hello, World!!  It's 401?") == "hello world it s 401"


def test_preprocess_lowercases_and_strips_punctuation():
    assert preprocess("WEBHOOK!!") == "webhook"


def test_preprocess_keeps_status_codes():
    assert "401" in preprocess("Why am I getting a 401 error?").split()


def test_preprocess_removes_stopwords():
    assert "the" not in preprocess("the webhook").split()


def test_preprocess_keeps_not_because_it_changes_the_meaning():
    assert "not" in preprocess("my webhook is NOT firing").split()


def test_preprocess_lemmatizes_words():
    words = preprocess("The servers were returning errors").split()
    assert "server" in words
    assert "error" in words


def test_preprocess_does_not_turn_cors_into_cor():
    assert "cors" in preprocess("CORS policy").split()
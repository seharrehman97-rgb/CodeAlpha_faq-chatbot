"""Compare tuning ideas one at a time, using the test set.

Run from the project folder:  python -m src.experiments
"""
import pandas as pd

from src import config
from src.chatbot import FAQChatbot
from src.evaluate import TEST_PATH, run_tests, summarize

# Very generic words that appear in many questions and carry little meaning.
GENERIC_WORDS = {"api", "request", "send", "error", "mean", "work", "use", "make", "tell", "explain"}

# The settings that mean "no tuning" (the original baseline).
DEFAULTS = {
    "EXTRA_STOPWORDS": set(),
    "USE_BIGRAMS": False,
    "MIN_COVERAGE": 0.0,
    "MIN_MARGIN": 0.0,
    "STRICT_CODES": False,
}

EXPERIMENTS = [
    ("0. Baseline (no changes)", {}),
    ("A. Extra stopwords", {"EXTRA_STOPWORDS": GENERIC_WORDS}),
    ("B. Word pairs (bigrams)", {"USE_BIGRAMS": True}),
    ("C. Coverage rule 50%", {"MIN_COVERAGE": 0.5}),
    ("D1. Margin rule 0.10", {"MIN_MARGIN": 0.10}),
    ("D2. Margin rule 0.20", {"MIN_MARGIN": 0.20}),
    ("E. Strict unknown codes", {"STRICT_CODES": True}),
    ("A+B", {"EXTRA_STOPWORDS": GENERIC_WORDS, "USE_BIGRAMS": True}),
    ("B+C+D1+E", {"USE_BIGRAMS": True, "MIN_COVERAGE": 0.5, "MIN_MARGIN": 0.10, "STRICT_CODES": True}),
    ("A+B+C+D1+E", {"EXTRA_STOPWORDS": GENERIC_WORDS, "USE_BIGRAMS": True,
                    "MIN_COVERAGE": 0.5, "MIN_MARGIN": 0.10, "STRICT_CODES": True}),
]


def apply_settings(overrides: dict) -> None:
    """Reset every tuning option to its default, then apply the overrides."""
    for name, value in {**DEFAULTS, **overrides}.items():
        setattr(config, name, value)


def main():
    test_df = pd.read_csv(TEST_PATH)
    rows = []
    for name, overrides in EXPERIMENTS:
        apply_settings(overrides)
        bot = FAQChatbot()  # rebuilt each time, because some options change the vectorizer
        s = summarize(run_tests(bot, test_df))
        rows.append({"experiment": name, **s})
        print(f"done: {name}")
    apply_settings({})  # leave config.py's behaviour untouched

    table = pd.DataFrame(rows).set_index("experiment")
    table = (table * 100).round(1)
    table.columns = ["correct %", "top-3 %", "wrong %", "missed %", "off-topic refused %", "overall %", "misleading %"]
    print("\n=== Experiment results (higher is better, except 'wrong' and 'missed') ===")
    print(table.to_string())
    print(f"\nBest overall: {table['overall %'].idxmax()} ({table['overall %'].max()}%)")
    print(f"Fewest misleading answers: {table['misleading %'].idxmin()} ({table['misleading %'].min()}%)")
    table.to_csv("docs/experiments.csv")
    print("\nSaved docs/experiments.csv")


if __name__ == "__main__":
    main()
"""Evaluate the chatbot on a separate test set (questions that are NOT in faqs.csv).

Run from the project folder:  python -m src.evaluate
"""
import matplotlib

matplotlib.use("Agg")  # draw charts straight to image files, no window needed
import matplotlib.pyplot as plt
import pandas as pd

from src import config
from src.chatbot import FAQChatbot

TEST_PATH = "data/test_questions.csv"
THRESHOLDS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60]


def run_tests(bot: FAQChatbot, test_df: pd.DataFrame) -> pd.DataFrame:
    """Ask the bot every test question and record what happened."""
    rows = []
    for _, t in test_df.iterrows():
        reply = bot.get_response(t["question"])
        rows.append(
            {
                "question": t["question"],
                "expected": t["expected_faq_id"],
                "answered": bool(reply["found"]),
                "got": reply["faq_id"],
                "top3": reply["top_faq_ids"],
                "score": round(reply["score"], 2),
            }
        )
    return pd.DataFrame(rows)


def outcome(row) -> str:
    """Label one test result in plain words."""
    if row["expected"] == "NONE":  # an out-of-scope question
        return "answered out-of-scope question" if row["answered"] else "correctly refused"
    if not row["answered"]:
        return "refused (missed)"
    return "correct" if row["got"] == row["expected"] else "wrong answer"


def summarize(results: pd.DataFrame) -> dict:
    """Turn per-question results into the key percentages."""
    in_scope = results[results["expected"] != "NONE"]
    out_scope = results[results["expected"] == "NONE"]
    labels = results.apply(outcome, axis=1)
    in_labels = labels[in_scope.index]
    top3_hit = in_scope.apply(lambda r: r["expected"] in r["top3"], axis=1)
    refused_ok = (labels[out_scope.index] == "correctly refused").sum()
    return {
        "correct": (in_labels == "correct").mean(),  # top-1 accuracy
        "top3": top3_hit.mean(),  # expected FAQ is among the 3 closest
        "wrong": (in_labels == "wrong answer").mean(),  # confident but wrong
        "missed": (in_labels == "refused (missed)").mean(),  # said "not sure" wrongly
        "oos_refused": refused_ok / len(out_scope),  # out-of-scope handled well
        "overall": ((in_labels == "correct").sum() + refused_ok) / len(results),
    }


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main():
    bot = FAQChatbot()
    test_df = pd.read_csv(TEST_PATH)
    n_out = int((test_df["expected_faq_id"] == "NONE").sum())
    print(f"Test set: {len(test_df) - n_out} in-scope + {n_out} out-of-scope questions")

    # 1. Results at the current threshold
    results = run_tests(bot, test_df)
    results["outcome"] = results.apply(outcome, axis=1)
    s = summarize(results)
    print(f"\n=== Results at threshold {config.THRESHOLD} ===")
    print(f"Top-1 accuracy (correct answer given):   {pct(s['correct'])}")
    print(f"Top-3 accuracy (right FAQ in top 3):     {pct(s['top3'])}")
    print(f"Wrong answer given confidently:          {pct(s['wrong'])}")
    print(f"Missed (bot said 'not sure'):            {pct(s['missed'])}")
    print(f"Out-of-scope questions refused:          {pct(s['oos_refused'])}")
    print(f"Overall good outcomes:                   {pct(s['overall'])}")

    # 2. Failures, for error analysis
    failures = results[~results["outcome"].isin(["correct", "correctly refused"])]
    print(f"\n=== {len(failures)} failures (use these for error analysis) ===")
    for _, r in failures.iterrows():
        print(f"[{r['outcome']}] {r['question']!r}")
        print(f"     expected {r['expected']}, got {r['got']}, score {r['score']}, top3 {r['top3']}")

    # 3. Try different thresholds
    original = config.THRESHOLD
    sweep = []
    for t in THRESHOLDS:
        config.THRESHOLD = t
        sweep.append({"threshold": t, **summarize(run_tests(bot, test_df))})
    config.THRESHOLD = original
    sweep_df = pd.DataFrame(sweep).set_index("threshold")
    print("\n=== Threshold comparison (percentages) ===")
    print((sweep_df * 100).round(1).to_string())
    best_t = sweep_df["overall"].idxmax()
    print(f"\nBest overall score at threshold {best_t} ({pct(sweep_df.loc[best_t, 'overall'])})")

    # 4. Save results and a chart for the README
    results.to_csv("docs/evaluation_results.csv", index=False)
    ax = (sweep_df[["correct", "wrong", "missed", "oos_refused", "overall"]] * 100).plot(
        marker="o", figsize=(8, 5)
    )
    ax.set_xlabel("Similarity threshold")
    ax.set_ylabel("Percent")
    ax.set_title("Effect of the threshold on chatbot results")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("docs/threshold_tradeoff.png", dpi=150)
    print("\nSaved docs/evaluation_results.csv and docs/threshold_tradeoff.png")


if __name__ == "__main__":
    main()
"""Show WHY the bot answered the way it did.

Run from the project folder:
    python -m src.explain "your question here"
"""
import sys

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src import config
from src.chatbot import FAQChatbot
from src.preprocess import preprocess


def explain(question: str) -> None:
    bot = FAQChatbot()
    matcher = bot.matcher
    clean = preprocess(question)
    words = clean.split()
    vocab = matcher.vectorizer.vocabulary_
    known = [w for w in words if w in vocab]
    unknown = [w for w in words if w not in vocab]

    print(f"Question:        {question!r}")
    print(f"After cleaning:  {clean!r}")
    print(f"Known words:     {known}")
    print(f"Unknown words:   {unknown}   (the FAQ data has never seen these)")
    print(f"Coverage:        {matcher.coverage(question):.0%}   (needs at least {config.MIN_COVERAGE:.0%})")

    # Score every FAQ question, then keep the best wording of the 3 closest FAQs.
    user_vec = matcher.vectorizer.transform([clean])
    sims = cosine_similarity(user_vec, matcher.faq_matrix).ravel()
    names = np.array(matcher.vectorizer.get_feature_names_out())
    seen, rows = set(), []
    for idx in sims.argsort()[::-1]:
        faq_id = matcher.df.iloc[idx]["faq_id"]
        if faq_id not in seen:
            seen.add(faq_id)
            rows.append(idx)
        if len(rows) == 3:
            break

    print("\nClosest FAQs:")
    for idx in rows:
        row = matcher.df.iloc[idx]
        # How much each shared word added to the score (they add up to the score).
        parts = user_vec.multiply(matcher.faq_matrix[idx]).toarray().ravel()
        top = [i for i in parts.argsort()[::-1][:4] if parts[i] > 0]
        because = ", ".join(f"{names[i]} ({parts[i]:.2f})" for i in top) or "nothing in common"
        print(f"  {sims[idx]:.2f}  [{row['faq_id']}] {row['question']}")
        print(f"        matched because of: {because}")

    gap = sims[rows[0]] - sims[rows[1]] if len(rows) > 1 else 0.0
    print(f"\nGap between 1st and 2nd FAQ: {gap:.2f}   (needs at least {config.MIN_MARGIN:.2f})")
    reply = bot.get_response(question)
    if reply["found"]:
        print(f"Decision: ANSWERED with {reply['faq_id']} (score {reply['score']:.2f})")
    else:
        print(f"Decision: did NOT answer. Bot said: {reply['answer'][:90]}...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python -m src.explain "your question here"')
    else:
        explain(" ".join(sys.argv[1:]))
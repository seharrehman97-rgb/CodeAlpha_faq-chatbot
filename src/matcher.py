"""Matching logic for the FAQ chatbot: TF-IDF vectors + cosine similarity."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocess import preprocess, preprocess_many


class FAQMatcher:
    def __init__(self, csv_path: str = "data/faqs.csv"):
        # Collect: load the FAQ table (one row per question wording).
        self.df = pd.read_csv(csv_path)
        # Preprocess: clean every FAQ question with the same function used for user input.
        clean_questions = preprocess_many(self.df["question"])
        # Vectorize: learn the vocabulary from the FAQ questions and turn each one into numbers.
        self.vectorizer = TfidfVectorizer()
        self.faq_matrix = self.vectorizer.fit_transform(clean_questions)

    def top_matches(self, user_question: str, n: int = 3) -> list[dict]:
        """Return the n closest FAQs (best first), at most one result per FAQ."""
        clean = preprocess(user_question)
        user_vector = self.vectorizer.transform([clean])
        scores = cosine_similarity(user_vector, self.faq_matrix).ravel()

        best_row_per_faq = {}
        for idx in scores.argsort()[::-1]:  # highest score first
            faq_id = self.df.iloc[idx]["faq_id"]
            if faq_id not in best_row_per_faq:
                best_row_per_faq[faq_id] = idx
            if len(best_row_per_faq) == n:
                break

        results = []
        for faq_id, idx in best_row_per_faq.items():
            row = self.df.iloc[idx]
            results.append(
                {
                    "faq_id": faq_id,
                    "category": row["category"],
                    "matched_question": row["question"],
                    "answer": row["answer"],
                    "source_url": row["source_url"],
                    "score": float(scores[idx]),
                }
            )
        return results

    def leave_one_out_accuracy(self) -> float:
        """Rough self-test: hide each question and check whether its closest
        neighbour belongs to the same FAQ."""
        sims = cosine_similarity(self.faq_matrix)
        np.fill_diagonal(sims, -1)  # a question must not match itself
        nearest = sims.argmax(axis=1)
        ids = self.df["faq_id"].to_numpy()
        return float((ids[nearest] == ids).mean())


if __name__ == "__main__":
    matcher = FAQMatcher()
    print(f"Loaded {len(matcher.df)} questions from {matcher.df['faq_id'].nunique()} FAQs")
    print(f"Rough self-test accuracy: {matcher.leave_one_out_accuracy():.1%}")

    samples = [
        "my token keeps getting rejected",
        "why is my webhook not working",
        "browser blocks my request from another domain",
        "server says bad gateway",
        "how many requests can i send per minute",
        "what is the weather today",
    ]
    for q in samples:
        print(f"\nUser: {q}")
        for r in matcher.top_matches(q, n=3):
            print(f"  {r['score']:.2f}  [{r['faq_id']}] {r['matched_question']}")
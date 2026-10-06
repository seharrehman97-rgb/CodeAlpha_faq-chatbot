"""The chatbot: combines preprocessing + matching and decides what to reply."""
import re

from src import config
from src.matcher import FAQMatcher

# Matches HTTP status codes such as 401, 404, 429, 502 (100-599).
STATUS_CODE = re.compile(r"\b[1-5]\d{2}\b")


class FAQChatbot:
    def __init__(self):
        self.matcher = FAQMatcher(config.FAQ_PATH)
        self.total_faqs = self.matcher.df["faq_id"].nunique()
        # The first row of each FAQ is its clean, main question (used for suggestions).
        self.titles = self.matcher.df.groupby("faq_id")["question"].first().to_dict()

    def get_response(self, user_text: str) -> dict:
        """Return a dict: found, answer, category, source_url, score, suggestions."""
        user_text = user_text.strip()
        if not user_text:
            return self._reply(False, "Please type a question.", [], 0.0)

        ranked = self.matcher.top_matches(user_text, n=self.total_faqs)

        # Shortcut: if the user typed a status code (e.g. 429), FAQs that
        # mention that code are moved to the front of the list.
        codes = set(STATUS_CODE.findall(user_text))
        code_hit = False
        if codes:
            with_code = [
                r for r in ranked
                if codes & set(STATUS_CODE.findall(r["matched_question"]))
            ]
            if with_code:
                code_hit = True
                others = [r for r in ranked if r not in with_code]
                ranked = with_code + others

        best = ranked[0]
        if code_hit or best["score"] >= config.THRESHOLD:
            related = self._suggest(ranked, start=1)
            return self._reply(True, best["answer"], related, best["score"], best)

        # Not confident: say so and offer the closest questions instead.
        suggestions = self._suggest(ranked, start=0)
        message = config.FALLBACK_MESSAGE if suggestions else config.OUT_OF_SCOPE_MESSAGE
        return self._reply(False, message, suggestions, best["score"])

    def _suggest(self, ranked: list, start: int) -> list:
        """Main questions of the next closest FAQs, skipping very weak matches."""
        chosen = ranked[start : start + config.NUM_SUGGESTIONS]
        return [
            self.titles[r["faq_id"]]
            for r in chosen
            if r["score"] >= config.MIN_SUGGESTION_SCORE
        ]

    @staticmethod
    def _reply(found, answer, suggestions, score, match=None) -> dict:
        return {
            "found": found,
            "answer": answer,
            "category": match["category"] if match else None,
            "source_url": match["source_url"] if match else None,
            "score": score,
            "suggestions": suggestions,
        }


def main():
    bot = FAQChatbot()
    print("REST API & Webhook Troubleshooter (type 'quit' to exit)")
    while True:
        text = input("\nYou: ").strip()
        if text.lower() in {"quit", "exit", "q"}:
            print("Bot: Goodbye!")
            break
        reply = bot.get_response(text)
        if reply["found"]:
            print(f"\nBot [{reply['category']}]: {reply['answer']}")
            print(f"Source: {reply['source_url']}")
            print(f"(match score: {reply['score']:.2f})")
            label = "Related questions:"
        else:
            print(f"\nBot: {reply['answer']}")
            label = "Did you mean:"
        if reply["suggestions"]:
            print(label)
            for s in reply["suggestions"]:
                print(f"  - {s}")


if __name__ == "__main__":
    main()

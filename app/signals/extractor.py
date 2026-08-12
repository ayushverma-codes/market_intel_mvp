# from dataclasses import dataclass

# from sklearn.feature_extraction.text import CountVectorizer


# @dataclass(frozen=True)
# class ExtractedSignal:
#     topic: str
#     entity: str | None = None


# class SignalExtractor:
#     def __init__(self, top_k: int = 5):
#         self.top_k = top_k

#     def extract(self, text: str) -> list[ExtractedSignal]:
#         vectorizer = CountVectorizer(
#             stop_words="english",
#             ngram_range=(1, 3),
#             min_df=1,
#             max_features=1000,
#             token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z-]{2,}\b",
#         )
#         matrix = vectorizer.fit_transform([text.lower()])
#         terms = vectorizer.get_feature_names_out()
#         counts = matrix.toarray()[0]
#         ranked = sorted(zip(terms, counts), key=lambda x: (-x[1], x[0]))
#         return [ExtractedSignal(topic=term) for term, count in ranked[: self.top_k] if count > 0]


import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class ExtractedSignal:
    topic: str


STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then",
    "than", "of", "to", "in", "on", "for", "from", "with",
    "by", "at", "as", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those",
    "it", "its", "their", "they", "them", "he", "she",
    "his", "her", "we", "our", "you", "your", "i", "me",
    "my", "after", "before", "during", "while", "about",
    "into", "over", "under", "between", "through",
    "against", "will", "would", "could", "should", "may",
    "might", "can", "must", "also", "just", "still",
    "already", "now", "today", "yesterday", "tomorrow",
    "said", "says", "say", "told", "according", "reported",
    "report", "reports", "news", "new", "latest",
}


GENERIC_WORDS = {
    "company", "companies",
    "business", "businesses",
    "city", "cities",
    "people", "person",
    "future", "challenge", "challenges",
    "expect", "expects", "expected",
    "higher", "high", "lower", "low",
    "coming", "apparent", "possible",
    "likely", "recent", "year", "years",
    "month", "months", "week", "weeks",
    "day", "days", "global", "world",
    "worldwide", "international",
    "online", "just", "big", "out",
}


# Core market-intelligence vocabulary.
DOMAIN_TERMS = {
    "food",
    "foods",
    "snack",
    "snacks",
    "beverage",
    "beverages",
    "drink",
    "drinks",
    "protein",
    "sugar",
    "health",
    "healthy",
    "nutrition",
    "consumer",
    "consumers",
    "retail",
    "retailer",
    "retailers",
    "price",
    "prices",
    "pricing",
    "cost",
    "costs",
    "demand",
    "supply",
    "market",
    "markets",
    "product",
    "products",
    "ingredient",
    "ingredients",
    "packaging",
    "inflation",
    "tariff",
    "tariffs",
    "trade",
    "sales",
    "spending",
    "growth",
    "decline",
    "investment",
    "manufacturing",
    "production",
    "ecommerce",
    "delivery",
    "restaurant",
    "restaurants",
    "grocery",
    "groceries",
    "supermarket",
    "supermarkets",
    "whey",
    "soy",
    "millet",
    "oats",
    "pea",
    "supply",
    "chain",
    "chains",
    "shortage",
    "shortages",
    "demand",
    "competition",
    "competitors",
}


class SignalExtractor:

    def __init__(
        self,
        top_k: int = 5,
        max_signals: int | None = None,
    ):
        self.top_k = top_k

        if max_signals is not None:
            self.top_k = max_signals

    def _clean_text(self, text: str) -> str:

        if not text:
            return ""

        text = BeautifulSoup(
            text,
            "html.parser",
        ).get_text(" ")

        text = text.lower()

        text = re.sub(
            r"https?://\S+",
            " ",
            text,
        )

        text = re.sub(
            r"[^a-z\s-]",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _valid_word(self, word: str) -> bool:

        if len(word) < 3:
            return False

        if word in STOPWORDS:
            return False

        if word in GENERIC_WORDS:
            return False

        return True

    def _extract_keywords(self, text: str) -> list[str]:

        words = text.split()

        keywords = []

        for word in words:

            if not self._valid_word(word):
                continue

            if word in DOMAIN_TERMS:
                keywords.append(word)

        return keywords

    def _extract_related_phrases(
        self,
        text: str,
    ) -> list[str]:

        words = text.split()

        signals = []

        for i, word in enumerate(words):

            if word not in DOMAIN_TERMS:
                continue

            # Look within a small context window.
            start = max(0, i - 4)
            end = min(len(words), i + 5)

            context = words[start:end]

            for candidate in context:

                if candidate == word:
                    continue

                if not self._valid_word(candidate):
                    continue

                if candidate in DOMAIN_TERMS:

                    phrase_words = sorted(
                        [word, candidate]
                    )

                    phrase = " ".join(
                        phrase_words
                    )

                    signals.append(phrase)

        return signals

    def extract(
        self,
        content: str,
    ) -> list[ExtractedSignal]:

        text = self._clean_text(content)

        if not text:
            return []

        phrases = self._extract_related_phrases(
            text
        )

        # Remove duplicates while preserving order.
        unique = list(
            dict.fromkeys(phrases)
        )

        results = []

        for phrase in unique:

            if len(results) >= self.top_k:
                break

            results.append(
                ExtractedSignal(
                    topic=phrase
                )
            )

        return results
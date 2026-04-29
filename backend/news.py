import os
import nltk
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon", quiet=True)

NEWS_API_URL = "https://newsapi.org/v2/everything"

_vader = SentimentIntensityAnalyzer()


def _score_sentiment(headlines: list[str]) -> int:
    """Average VADER compound scores and scale to [0, 10]."""
    if not headlines:
        return 0
    scores = [_vader.polarity_scores(h)["compound"] for h in headlines]
    average = sum(scores) / len(scores)
    return round((average + 1) * 5)


def _fetch_headlines(query: str, api_key: str, sort: str = "relevancy") -> list[str]:
    """
    Single NewsAPI request.  Returns a (possibly empty) list of headline strings.
    Using 'relevancy' as the default sort finds city-specific articles more
    reliably than 'publishedAt', which favours volume over topicality.
    """
    try:
        r = requests.get(
            NEWS_API_URL,
            params={
                "q":        query,
                "pageSize": 5,
                "sortBy":   sort,
                "language": "en",
                "apiKey":   api_key,
            },
            timeout=10,
        )
        r.raise_for_status()
        articles = r.json().get("articles", [])
        return [a["title"] for a in articles if a.get("title")]
    except (requests.RequestException, KeyError):
        return []


def get_news(city: str, country: str = "") -> dict:
    """
    Fetch up to 5 English news headlines for a city and score their sentiment
    with VADER.

    Search strategy (stops as soon as results are found):
      1. "{city} {country}" sorted by relevancy  — most specific
      2. "{city}" sorted by relevancy             — wider net (same language)
      3. "{city}" sorted by publishedAt           — catches very recent coverage

    Always returns a dict (never None) so callers always get a consistent type.

    Returns:
        {
            "headlines":       list[str] — 0-5 headline strings,
            "sentiment_score": int       — VADER score in [-5, 5],
        }
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("Error: NEWS_API_KEY not set.")
        return {"headlines": [], "sentiment_score": 0}

    combined = f"{city} {country}".strip() if country else city

    # Try progressively broader queries until we get articles
    for query, sort in [
        (combined, "relevancy"),
        (city,     "relevancy"),
        (city,     "publishedAt"),
    ]:
        headlines = _fetch_headlines(query, api_key, sort)
        if headlines:
            return {
                "headlines":       headlines,
                "sentiment_score": _score_sentiment(headlines),
            }

    return {"headlines": [], "sentiment_score": 0}

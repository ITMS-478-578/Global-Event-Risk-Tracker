import os
import requests

NEWS_API_URL = "https://newsapi.org/v2/everything"

NEGATIVE_WORDS = {"protest", "attack", "war", "conflict", "crisis", "riot", "shooting", "bomb", "terror", "disaster"}
POSITIVE_WORDS = {"festival", "growth", "peace", "celebration", "tourism", "development", "award", "record", "boom"}


def _score_sentiment(headlines: list[str]) -> int:
    """
    Assign a sentiment score by scanning headlines for keyword signals.

    Each negative keyword hit subtracts 1; each positive hit adds 1.
    The score is clamped to [-5, 5] so a single headline spike can't
    dominate the final Travel Readiness Score.
    """
    score = 0
    for headline in headlines:
        words = set(headline.lower().split())
        score -= len(words & NEGATIVE_WORDS)
        score += len(words & POSITIVE_WORDS)
    return max(-5, min(5, score))


def get_news(city: str) -> dict | None:
    """
    Fetch the top 5 news headlines for a city using the NewsAPI.

    Requires the environment variable NEWS_API_KEY to be set.

    Returns:
        {
            "headlines":       list[str] — up to 5 headline strings,
            "sentiment_score": int       — clamped to [-5, 5],
                                           negative = bad news, positive = good news,
        }
        or None if the API key is missing or the request fails.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("Error: NEWS_API_KEY environment variable not set.")
        return None

    try:
        response = requests.get(
            NEWS_API_URL,
            params={
                "q": city,
                "pageSize": 5,
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": api_key,
            },
            timeout=10,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])

        headlines = [article["title"] for article in articles if article.get("title")]

        return {
            "headlines": headlines,
            "sentiment_score": _score_sentiment(headlines),
        }

    except (requests.RequestException, KeyError):
        return None

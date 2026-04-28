import requests


def get_news_headlines(city: str, api_key: str, max_results: int = 5) -> list[dict]:
    """
    Fetch recent news headlines related to a city using the NewsAPI.

    Each item in the returned list contains:
        - title (str): headline text
        - source (str): name of the news outlet
        - url (str): link to the full article
        - published_at (str): ISO 8601 timestamp

    Returns an empty list if the request fails or no articles are found.
    """
    pass

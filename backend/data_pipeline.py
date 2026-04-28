import pandas as pd

from backend.weather import get_weather
from backend.news import get_news_headlines
from backend.currency import get_exchange_rate
from backend.safety import get_safety_score
from backend.scoring import calculate_travel_score


def fetch_all_data(city: str, api_keys: dict) -> dict:
    """
    Orchestrate all API calls for a given city and return a unified data dict.

    api_keys should contain:
        - "weather":  OpenWeatherMap key
        - "news":     NewsAPI key
        - "currency": ExchangeRate-API key
        - "places":   Google Places key

    Returns the result of calculate_travel_score() enriched with raw API data
    under the keys "weather_raw", "news_raw", and "hospitals_raw".
    """
    pass


def save_result_to_csv(city: str, score_data: dict, filepath: str = "data/city_scores.csv") -> None:
    """
    Append a city's score result to the historical CSV log.

    Columns written: city, score, verdict, timestamp.
    Creates the file with a header row if it does not yet exist.
    """
    pass


def load_history(filepath: str = "data/city_scores.csv") -> pd.DataFrame:
    """
    Load the historical city-scores CSV into a pandas DataFrame.

    Returns an empty DataFrame with the expected columns if the file
    does not exist yet, so callers never have to handle a missing-file error.
    """
    pass

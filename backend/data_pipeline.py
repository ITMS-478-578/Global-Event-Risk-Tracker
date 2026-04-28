import os
from datetime import datetime

import pandas as pd

from backend.weather import get_weather
from backend.news import get_news
from backend.currency import get_exchange_rate
from backend.safety import get_safety_score
from backend.scoring import calculate_travel_score

CSV_PATH = "data/city_scores.csv"

COLUMNS = [
    "city",
    "final_score",
    "weather_weight",
    "safety_weight",
    "news_weight",
    "exchange_weight",
    "timestamp",
]


def load_history(filepath: str = CSV_PATH) -> pd.DataFrame:
    """
    Load the city-scores CSV into a DataFrame.

    Returns an empty DataFrame with the correct columns when the file does
    not yet exist, so every caller always gets a valid DataFrame back.
    """
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame(columns=COLUMNS)


def build_city_dataframe(city: str, scores_dict: dict, filepath: str = CSV_PATH) -> pd.DataFrame:
    """
    Persist a city's scores to the CSV log and return the updated DataFrame.

    scores_dict must be the dict returned by calculate_travel_score(), i.e.:
        {
            "final_score": int,
            "breakdown": {
                "weather_weight":  int,
                "safety_weight":   int,
                "news_weight":     int,
                "exchange_weight": int,
            }
        }

    Behaviour:
        - Creates the CSV (and the data/ directory) if they don't exist yet.
        - Replaces any existing row for the same city (case-insensitive),
          so re-searching a city updates its record rather than duplicating it.
        - Returns the full updated DataFrame after saving.
    """
    breakdown = scores_dict.get("breakdown", {})

    new_row = pd.DataFrame([{
        "city":            city.strip().title(),
        "final_score":     scores_dict.get("final_score", 0),
        "weather_weight":  breakdown.get("weather_weight", 0),
        "safety_weight":   breakdown.get("safety_weight", 0),
        "news_weight":     breakdown.get("news_weight", 0),
        "exchange_weight": breakdown.get("exchange_weight", 0),
        "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M"),
    }])

    df = load_history(filepath)

    # Drop any existing row for this city (case-insensitive match).
    df = df[df["city"].str.lower() != city.strip().lower()]

    df = pd.concat([df, new_row], ignore_index=True)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)

    return df


def fetch_all_data(city: str, currency_code: str = "USD") -> dict:
    """
    Run all four API modules for a city and return the combined result.

    Args:
        city:          City name to analyse.
        currency_code: 3-letter ISO code for the local currency (default "USD").

    Returns a dict with:
        "score_result"   — output of calculate_travel_score()
        "weather_raw"    — raw weather dict (or None)
        "news_raw"       — raw news dict    (or None)
        "currency_raw"   — raw currency dict (or None)
        "safety_raw"     — raw safety dict   (or None)
    """
    weather  = get_weather(city)
    news     = get_news(city)
    currency = get_exchange_rate(currency_code)
    safety   = get_safety_score(city)

    score_result = calculate_travel_score(weather, news, currency, safety)

    return {
        "score_result": score_result,
        "weather_raw":  weather,
        "news_raw":     news,
        "currency_raw": currency,
        "safety_raw":   safety,
    }

import os
from datetime import datetime

from dotenv import load_dotenv

from backend.weather import get_weather
from backend.news import get_news
from backend.currency import get_exchange_rate
from backend.safety import get_safety_score
from backend.scoring import calculate_travel_score

load_dotenv()

def load_api_key(env_var: str) -> str:
    """
    Read an API key from an environment variable.
    Raises EnvironmentError early so misconfiguration surfaces at startup,
    not buried inside an API call.
    """
    key = os.getenv(env_var)
    if not key:
        raise EnvironmentError(f"Missing required environment variable: {env_var}")
    return key


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def format_timestamp(iso_string: str) -> str:
    """
    Convert an ISO 8601 string (e.g. "2024-06-01T14:30:00Z") to a
    human-readable form (e.g. "June 1, 2024 at 2:30 PM").
    Returns the original string unchanged if parsing fails.
    """
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%B %-d, %Y at %-I:%M %p")
    except (ValueError, AttributeError):
        return iso_string

def _fmt_weather(data: dict | None) -> str:
    if not data:
        return "Weather data unavailable."
    return f"{data['temperature']:.1f}°C  —  {data['weather_description']}"


def _fmt_safety(data: dict | None) -> str:
    if not data:
        return "Safety data unavailable."
    return (
        f"Hospitals: {data['hospital_count']}    Police stations: {data['police_count']}\n"
        f"Safety score: {data['safety_score']} / 100"
    )


def _fmt_news(data: dict | None) -> str:
    if not data or not data.get("headlines"):
        return "No headlines found."
    bullets = "\n".join(f"• {h}" for h in data["headlines"])
    return f"{bullets}\n\nSentiment: {data['sentiment_score']:+d} / 5"


def _fmt_currency(data: dict | None, currency_code: str) -> str:
    if not data:
        return "Exchange rate unavailable."
    return (
        f"1 USD = {data['rate']:.4f} {currency_code.upper()}\n"
        f"Stability score: {data['score']} / 100"
    )


def analyze_city(city: str, currency_code: str = "USD") -> dict:
    """
    Fetch all data sources for a city and return a dict the GUI can consume
    directly — no further processing required in main.py.
    Return dict keys:
        For update_dashboard():
            "score"                    — int 0-100 final travel readiness score
            "Weather Forecast"         — formatted string for the weather card
            "Local Safety (Hospitals)" — formatted string for the safety card
            "Recent News Headlines"    — formatted string for the news card
            "Exchange Rate (USD)"      — formatted string for the currency card
        For generate_city_chart():
            "weather_weight"   — int, points contributed by weather  (0-25)
            "safety_weight"    — int, points contributed by safety   (0-30)
            "news_weight"      — int, points contributed by news     (0-25)
            "exchange_weight"  — int, points contributed by currency (0-20)
    Every key is always present. If an API fails its card shows a graceful
    fallback message rather than crashing the GUI.
    """
    weather  = get_weather(city)
    news     = get_news(city)
    currency = get_exchange_rate(currency_code)
    safety   = get_safety_score(city)   # never None 

    result    = calculate_travel_score(weather, news, currency, safety)
    breakdown = result["breakdown"]

    return {
        #Score (drives card colour and label in update_dashboard)
        "score": result["final_score"],

        #GUI card strings (keys must match create_data_card() titles exactly)
        "Weather Forecast":          _fmt_weather(weather),
        "Local Safety (Hospitals)":  _fmt_safety(safety),
        "Recent News Headlines":     _fmt_news(news),
        "Exchange Rate (USD)":       _fmt_currency(currency, currency_code),

        #Chart weights (used by generate_city_chart)
        "weather_weight":  breakdown["weather_weight"],
        "safety_weight":   breakdown["safety_weight"],
        "news_weight":     breakdown["news_weight"],
        "exchange_weight": breakdown["exchange_weight"],
    }

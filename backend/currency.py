import os
import math
import requests

EXCHANGERATE_URL = "https://api.exchangerate.host/live"


def _rate_to_score(rate: float) -> int:
    """
    Convert an exchange rate (units of foreign currency per 1 USD) to a
    currency-stability score between 0 and 100.
    Uses a log10 scale so the full range of currencies (0.1 → 25 000+)
    compresses into a readable 0-100 band
    """
    score = 80 - (math.log10(max(rate, 0.01)) * 15)
    return max(0, min(100, round(score)))


def get_exchange_rate(currency: str) -> dict | None:
    """
    Fetch the current exchange rate for a currency against USD using
    the exchangerate.host API.
    Returns:
        {
            "rate":  float — units of `currency` per 1 USD,
            "score": int   — stability score 0-100
                            (higher = stronger / more stable relative to USD),
        }
        or None if the API key is missing or the request fails.
    """
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    if not api_key:
        print("Error: EXCHANGERATE_API_KEY environment variable not set.")
        return None

    currency = currency.upper().strip()

    try:
        response = requests.get(
            EXCHANGERATE_URL,
            params={
                "access_key": api_key,
                "currencies": currency,
                "source": "USD",
                "format": 1,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            print(f"API error: {data.get('error', {}).get('info', 'Unknown error')}")
            return None

        quote_key = f"USD{currency}"
        rate = data["quotes"].get(quote_key)

        if rate is None:
            print(f"Currency '{currency}' not found in API response.")
            return None

        return {
            "rate": round(rate, 6),
            "score": _rate_to_score(rate),
        }

    except (requests.RequestException, KeyError):
        return None

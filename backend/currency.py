import math
import requests

# open.er-api.com — completely free, no API key, no rate-limit issues.
OPEN_ER_URL = "https://open.er-api.com/v6/latest/USD"


def _rate_to_score(rate: float) -> int:
    """
    Convert an exchange rate (units of foreign currency per 1 USD) to a
    currency-stability score between 0 and 100.
    Uses a log10 scale so the full range of currencies (0.1 → 25 000+)
    compresses into a readable 0-100 band.
    """
    score = 80 - (math.log10(max(rate, 0.01)) * 15)
    return max(0, min(100, round(score)))


def get_exchange_rate(currency: str) -> dict | None:
    """
    Fetch the current exchange rate for a currency against USD.
    Uses the open.er-api.com free API — no key required.

    Special case: if currency is "USD", returns a base-currency sentinel
    so the display layer can show a meaningful message instead of "1 USD = 1 USD".

    Returns:
        {
            "rate":     float — units of currency per 1 USD,
            "score":    int   — stability score 0-100,
            "is_base":  bool  — True when currency == USD,
        }
        or None if the request fails or the currency code is unknown.
    """
    currency = currency.upper().strip()

    if currency == "USD":
        return {"rate": 1.0, "score": 80, "is_base": True}

    try:
        response = requests.get(OPEN_ER_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return None

        rate = data["rates"].get(currency)
        if rate is None:
            print(f"Currency '{currency}' not found.")
            return None

        return {
            "rate":    round(rate, 4),
            "score":   _rate_to_score(rate),
            "is_base": False,
        }

    except (requests.RequestException, KeyError, AttributeError):
        return None

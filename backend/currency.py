import requests


def get_exchange_rate(base_currency: str, target_currency: str, api_key: str) -> float | None:
    """
    Fetch the current exchange rate between two currencies using the ExchangeRate-API.

    Args:
        base_currency:   3-letter code of the source currency (e.g. "USD").
        target_currency: 3-letter code of the destination currency (e.g. "EUR").
        api_key:         API key for the exchange rate service.

    Returns the rate as a float (e.g. 0.92 means 1 USD = 0.92 EUR),
    or None if the request fails.
    """
    pass

import requests


def get_nearby_hospitals(city: str, api_key: str, radius_meters: int = 5000) -> list[dict]:
    """
    Find hospitals and medical facilities near a city using the Google Places API.

    Each item in the returned list contains:
        - name (str): facility name
        - address (str): formatted street address
        - rating (float | None): Google rating (1.0–5.0), if available
        - open_now (bool | None): whether the place is currently open

    Returns an empty list if the request fails or no results are found.
    """
    pass


def get_safety_score(city: str) -> int:
    """
    Derive a safety score (0–100) for a city based on hospital density
    and any available crime-index data.

    Higher values indicate safer conditions for travelers.
    Returns 50 as a neutral default when data is unavailable.
    """
    pass

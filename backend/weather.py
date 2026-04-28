import requests


def get_weather(city: str, api_key: str) -> dict:
    """
    Fetch current weather data for a given city using the OpenWeatherMap API.

    Returns a dict with keys:
        - temperature (float): current temp in Celsius
        - condition (str): e.g. "Clear", "Rain"
        - humidity (int): percentage
        - description (str): human-readable summary

    Returns an empty dict if the request fails.
    """
    pass

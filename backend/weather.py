import requests

#Maps WMO weather interpretation codes to human-readable descriptions.
#Full code list: https://open-meteo.com/en/docs#weathervariables
WMO_CODES = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2:  "Partly cloudy",
    3:  "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

HEADERS = {"User-Agent": "GlobalEventRiskTracker/1.0"}


def _geocode(city: str) -> tuple[float, float] | None:
    """
    Convert a city name to (latitude, longitude) using the Nominatim API.
    Returns None if the city cannot be found or the request fails.
    """
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])
    except (requests.RequestException, KeyError, ValueError):
        return None


def get_weather(city: str, coords: tuple[float, float] | None = None) -> dict | None:
    """
    Fetch current weather for a city using Open-Meteo (no API key required).

    Args:
        city:   City name (used for geocoding if coords are not provided).
        coords: Optional pre-computed (lat, lon) — skips the Nominatim call
                when the caller has already geocoded the city.
    Returns:
        {"temperature": float, "weather_description": str}
        or None if geocoding or the weather request fails.
    """
    if coords is None:
        coords = _geocode(city)
    if coords is None:
        return None

    lat, lon = coords

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weathercode",
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        temperature = current["temperature_2m"]
        code = current["weathercode"]
        description = WMO_CODES.get(code, "Unknown condition")

        return {
            "temperature": temperature,
            "weather_description": description,
        }

    except (requests.RequestException, KeyError):
        return None

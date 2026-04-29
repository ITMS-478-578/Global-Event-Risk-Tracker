import os
import requests
from datetime import datetime

from dotenv import load_dotenv

from backend.weather import get_weather
from backend.news import get_news
from backend.currency import get_exchange_rate
from backend.safety import get_safety_score
from backend.scoring import calculate_travel_score
from backend.ai_analysis import get_city_analysis

load_dotenv()

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "GlobalEventRiskTracker/1.0"}

# ISO 3166-1 alpha-2 country code → ISO 4217 currency code
COUNTRY_CURRENCY = {
    "AD": "EUR", "AE": "AED", "AF": "AFN", "AG": "XCD", "AL": "ALL",
    "AM": "AMD", "AO": "AOA", "AR": "ARS", "AT": "EUR", "AU": "AUD",
    "AZ": "AZN", "BA": "BAM", "BB": "BBD", "BD": "BDT", "BE": "EUR",
    "BF": "XOF", "BG": "BGN", "BH": "BHD", "BI": "BIF", "BJ": "XOF",
    "BN": "BND", "BO": "BOB", "BR": "BRL", "BS": "BSD", "BT": "BTN",
    "BW": "BWP", "BY": "BYN", "BZ": "BZD", "CA": "CAD", "CD": "CDF",
    "CF": "XAF", "CG": "XAF", "CH": "CHF", "CI": "XOF", "CL": "CLP",
    "CM": "XAF", "CN": "CNY", "CO": "COP", "CR": "CRC", "CU": "CUP",
    "CV": "CVE", "CY": "EUR", "CZ": "CZK", "DE": "EUR", "DJ": "DJF",
    "DK": "DKK", "DO": "DOP", "DZ": "DZD", "EC": "USD", "EE": "EUR",
    "EG": "EGP", "ER": "ERN", "ES": "EUR", "ET": "ETB", "FI": "EUR",
    "FJ": "FJD", "FR": "EUR", "GA": "XAF", "GB": "GBP", "GE": "GEL",
    "GH": "GHS", "GM": "GMD", "GN": "GNF", "GQ": "XAF", "GR": "EUR",
    "GT": "GTQ", "GW": "XOF", "GY": "GYD", "HN": "HNL", "HR": "EUR",
    "HT": "HTG", "HU": "HUF", "ID": "IDR", "IE": "EUR", "IL": "ILS",
    "IN": "INR", "IQ": "IQD", "IR": "IRR", "IS": "ISK", "IT": "EUR",
    "JM": "JMD", "JO": "JOD", "JP": "JPY", "KE": "KES", "KG": "KGS",
    "KH": "KHR", "KI": "AUD", "KM": "KMF", "KW": "KWD", "KZ": "KZT",
    "LA": "LAK", "LB": "LBP", "LI": "CHF", "LK": "LKR", "LR": "LRD",
    "LS": "LSL", "LT": "EUR", "LU": "EUR", "LV": "EUR", "LY": "LYD",
    "MA": "MAD", "MC": "EUR", "MD": "MDL", "ME": "EUR", "MG": "MGA",
    "MH": "USD", "MK": "MKD", "ML": "XOF", "MM": "MMK", "MN": "MNT",
    "MR": "MRU", "MT": "EUR", "MU": "MUR", "MV": "MVR", "MW": "MWK",
    "MX": "MXN", "MY": "MYR", "MZ": "MZN", "NA": "NAD", "NE": "XOF",
    "NG": "NGN", "NI": "NIO", "NL": "EUR", "NO": "NOK", "NP": "NPR",
    "NR": "AUD", "NZ": "NZD", "OM": "OMR", "PA": "PAB", "PE": "PEN",
    "PG": "PGK", "PH": "PHP", "PK": "PKR", "PL": "PLN", "PT": "EUR",
    "PW": "USD", "PY": "PYG", "QA": "QAR", "RO": "RON", "RS": "RSD",
    "RU": "RUB", "RW": "RWF", "SA": "SAR", "SB": "SBD", "SC": "SCR",
    "SD": "SDG", "SE": "SEK", "SG": "SGD", "SI": "EUR", "SK": "EUR",
    "SL": "SLL", "SM": "EUR", "SN": "XOF", "SO": "SOS", "SR": "SRD",
    "SS": "SSP", "ST": "STN", "SV": "USD", "SY": "SYP", "SZ": "SZL",
    "TD": "XAF", "TG": "XOF", "TH": "THB", "TJ": "TJS", "TL": "USD",
    "TM": "TMT", "TN": "TND", "TO": "TOP", "TR": "TRY", "TT": "TTD",
    "TW": "TWD", "TZ": "TZS", "UA": "UAH", "UG": "UGX", "US": "USD",
    "UY": "UYU", "UZ": "UZS", "VA": "EUR", "VE": "VES", "VN": "VND",
    "VU": "VUV", "WS": "WST", "YE": "YER", "ZA": "ZAR", "ZM": "ZMW",
    "ZW": "ZWL",
}


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

def geocode_city(city: str) -> dict | None:
    """
    Resolve a city name to coordinates and country info via Nominatim.

    Making ONE geocoding call per search (instead of one per module) avoids
    hitting Nominatim's 1 req/s rate limit and eliminates ambiguity — every
    downstream module uses the same resolved location.

    Returns:
        {lat, lon, country_code (ISO 3166-1 alpha-2 uppercase), country_name}
        or None if the city cannot be resolved.
    """
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1, "addressdetails": 1},
            # Accept-Language forces English country names from Nominatim,
            # preventing non-Latin scripts (Thai, Arabic, etc.) from appearing
            # in chart titles and triggering matplotlib glyph warnings.
            headers={**HEADERS, "Accept-Language": "en-US,en;q=0.9"},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            return None
        r = results[0]
        address = r.get("address", {})
        return {
            "lat":          float(r["lat"]),
            "lon":          float(r["lon"]),
            "country_code": address.get("country_code", "").upper(),
            "country_name": address.get("country", ""),
        }
    except (requests.RequestException, KeyError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def load_api_key(env_var: str) -> str:
    """Read an API key from the environment; raise early on misconfiguration."""
    key = os.getenv(env_var)
    if not key:
        raise EnvironmentError(f"Missing required environment variable: {env_var}")
    return key


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def format_timestamp(iso_string: str) -> str:
    """Convert ISO 8601 → human-readable; return original string on failure."""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%B %-d, %Y at %-I:%M %p")
    except (ValueError, AttributeError):
        return iso_string


# ---------------------------------------------------------------------------
# Display formatters
# ---------------------------------------------------------------------------

def _fmt_weather(data: dict | None) -> str:
    if not data:
        return "Weather data unavailable."
    c = data["temperature"]
    f = round(c * 9 / 5 + 32, 1)
    return f"{c:.1f}°C / {f}°F  —  {data['weather_description']}"


def _fmt_safety(data: dict | None) -> str:
    if not data:
        return "Safety data unavailable."
    score = data.get("safety_score", 50)
    h     = data.get("hospital_count")
    p      = data.get("police_count")

    lines = [f"Safety score: {score} / 100  (Global Peace Index)"]
    if h is not None and p is not None:
        lines.insert(0, f"Hospitals: {h}    Police stations: {p}")
    return "\n".join(lines)


def _fmt_news(data: dict | None) -> str:
    if not data or not data.get("headlines"):
        return "No headlines found."
    bullets = "\n".join(f"• {h}" for h in data["headlines"])
    return f"{bullets}\n\nSentiment: {data['sentiment_score']:+d} / 5"


def _fmt_currency(data: dict | None, currency_code: str) -> str:
    if not data:
        return "Exchange rate unavailable."
    if data.get("is_base"):
        return f"Destination uses USD — no conversion needed.\nStability score: {data['score']} / 100"
    return (
        f"1 USD = {data['rate']:.4f} {currency_code.upper()}\n"
        f"Stability score: {data['score']} / 100"
    )


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def analyze_city(city: str) -> dict:
    """
    Fetch all data for a city and return a dict ready for the GUI.

    Geocodes the city once and passes the result to every downstream module,
    which avoids multiple Nominatim calls (rate limit) and ensures all modules
    agree on the same resolved location (disambiguation fix for cities like
    'Mandalay' that share names with other places).

    Currency is auto-detected from the city's country — no manual input needed.

    Return keys:
        score, "Weather Forecast", "Local Safety (Hospitals)",
        "Recent News Headlines", "Exchange Rate (USD)",
        weather_weight, safety_weight, news_weight, exchange_weight,
        weather_raw_score, safety_raw_score, news_raw_score, currency_raw_score,
        country, currency_code, ai_summary
    """
    # --- Single geocoding call ---
    geo          = geocode_city(city)
    coords       = (geo["lat"], geo["lon"]) if geo else None
    country_code = geo["country_code"]  if geo else ""
    country_name = geo["country_name"]  if geo else ""
    currency_code = COUNTRY_CURRENCY.get(country_code, "USD")

    # --- Fetch (each returns None / fallback on failure) ---
    weather  = get_weather(city, coords=coords)
    news     = get_news(city, country=country_name)
    currency = get_exchange_rate(currency_code)
    safety   = get_safety_score(coords=coords, country_code=country_code)

    # --- Score ---
    result    = calculate_travel_score(weather, news, currency, safety)
    breakdown = result["breakdown"]
    raw       = result.get("raw_scores", {})

    out = {
        "score": result["final_score"],

        # Card strings (keys must match create_data_card() titles exactly)
        "Weather Forecast":          _fmt_weather(weather),
        "Local Safety":  _fmt_safety(safety),
        "Recent News Headlines":     _fmt_news(news),
        "Exchange Rate (USD)":       _fmt_currency(currency, currency_code),

        # Chart weights
        "weather_weight":  breakdown["weather_weight"],
        "safety_weight":   breakdown["safety_weight"],
        "news_weight":     breakdown["news_weight"],
        "exchange_weight": breakdown["exchange_weight"],

        # Raw 0-100 scores for the radar chart
        "weather_raw_score":  raw.get("weather",  50),
        "safety_raw_score":   raw.get("safety",   50),
        "news_raw_score":     raw.get("news",     50),
        "currency_raw_score": raw.get("currency", 50),

        "country":       country_name,
        "currency_code": currency_code,
    }

    # --- AI summary (runs inside the background thread) ---
    try:
        out["ai_summary"] = get_city_analysis(city, country_name, out)
    except Exception:
        out["ai_summary"] = ""

    return out

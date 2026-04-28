NEUTRAL = 50  #fallback score when a module returned None
#Condition keywords mapped to a quality score (0–100).
#Checked in order first match wins, so "heavy" before "rain" matters.
_CONDITION_SCORES: list[tuple[str, int]] = [
    ("thunderstorm", 10),
    ("heavy rain",   20),
    ("heavy snow",   20),
    ("freezing",     25),
    ("violent",      15),
    ("snow",         35),
    ("rain",         40),
    ("drizzle",      45),
    ("fog",          50),
    ("overcast",     65),
    ("partly cloudy", 82),
    ("mainly clear", 92),
    ("clear",        100),
]


def _weather_condition_score(description: str) -> int:
    desc = description.lower()
    for keyword, score in _CONDITION_SCORES:
        if keyword in desc:
            return score
    return NEUTRAL


def _temperature_score(temp_c: float) -> int:
    """
    Score how comfortable the temperature is for a traveler.
    Ideal band is 18–25 °C; scores fall off symmetrically toward extremes.
    """
    if 18 <= temp_c <= 25:
        return 100
    if 10 <= temp_c < 18 or 25 < temp_c <= 32:
        return 72
    if 0 <= temp_c < 10 or 32 < temp_c <= 38:
        return 45
    return 20  # below 0 °C or above 38 °C


def _weather_score(weather: dict | None) -> int:
    """Combine temperature comfort and sky condition into a 0–100 score."""
    if not weather:
        return NEUTRAL
    temp_s = _temperature_score(weather.get("temperature", 20))
    cond_s = _weather_condition_score(weather.get("weather_description", ""))
    return round((temp_s + cond_s) / 2)


def _news_score(news: dict | None) -> int:
    """
    Normalize the news sentiment from [-5, 5] to [0, 100].
    Formula: (sentiment + 5) × 10
    """
    if not news:
        return NEUTRAL
    raw = news.get("sentiment_score", 0)
    return max(0, min(100, (raw + 5) * 10))


def calculate_travel_score(
    weather: dict | None,
    news: dict | None,
    currency: dict | None,
    safety: dict | None,
) -> dict:
    """
    Combine outputs from all four backend modules into a final Travel
    Readiness Score using fixed weights.
    Weights:
        Safety:   30 %  (0–30 points)
        Weather:  25 %  (0–25 points)
        News:     25 %  (0–25 points)
        Currency: 20 %  (0–20 points)
    Each module may pass None (API failure) — a neutral score of 50 is
    used so a single outage doesn't collapse the overall result.
    Returns:
        {
            "final_score": int,          — 0–100 overall score
            "breakdown": {
                "weather_weight":  int,  — points contributed by weather  (0–25)
                "safety_weight":   int,  — points contributed by safety   (0–30)
                "news_weight":     int,  — points contributed by news     (0–25)
                "exchange_weight": int,  — points contributed by currency (0–20)
            }
        }
    """
    weather_s  = _weather_score(weather)
    safety_s   = safety["safety_score"] if safety else NEUTRAL
    news_s     = _news_score(news)
    currency_s = currency["score"] if currency else NEUTRAL

    weather_weight  = round(weather_s  * 0.25)
    safety_weight   = round(safety_s   * 0.30)
    news_weight     = round(news_s     * 0.25)
    exchange_weight = round(currency_s * 0.20)

    final_score = max(0, min(100, weather_weight + safety_weight + news_weight + exchange_weight))

    return {
        "final_score": final_score,
        "breakdown": {
            "weather_weight":  weather_weight,
            "safety_weight":   safety_weight,
            "news_weight":     news_weight,
            "exchange_weight": exchange_weight,
        },
    }

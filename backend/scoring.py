def calculate_travel_score(weather: dict, news: list[dict], exchange_rate: float | None, safety_score: int) -> dict:
    """
    Combine data from all API modules into a single Travel Readiness Score.

    Weights (adjustable):
        - Weather:       30 %
        - Safety:        30 %
        - News sentiment: 25 %
        - Exchange rate:  15 %

    Returns a dict with:
        - score (int):           overall score 0–100
        - weather_weight (float): weather contribution (0–30)
        - safety_weight (float):  safety contribution (0–30)
        - news_weight (float):    news contribution (0–25)
        - exchange_weight (float):exchange-rate contribution (0–15)
        - verdict (str):          "Safe", "Moderate Risk", or "High Risk"
    """
    pass

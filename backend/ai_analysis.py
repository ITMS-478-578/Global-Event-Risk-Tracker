import os
import anthropic


def get_city_analysis(city: str, country: str, data: dict) -> str:
    """
    Send city metrics to Claude and return an AI-written travel intelligence summary.

    Requires ANTHROPIC_API_KEY in the environment (or .env file).
    Returns a fallback string if the key is missing or the API call fails.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    score   = data.get("score", 0)
    verdict = "safe" if score > 75 else "moderate risk" if score > 50 else "high risk"
    location = f"{city}, {country}" if country else city

    prompt = f"""You are a concise travel intelligence analyst. Based on the real-time data below, write a practical travel assessment for {location}.

Travel Readiness Score: {score}/100 ({verdict})
Weather: {data.get("Weather Forecast", "N/A")}
Safety Infrastructure: {data.get("Local Safety (Hospitals)", "N/A")}
Recent Headlines: {data.get("Recent News Headlines", "N/A")}
Currency: {data.get("Exchange Rate (USD)", "N/A")}

Write exactly 3 short paragraphs:
1. Overall recommendation based on the score.
2. Key risks or concerns a traveler should know.
3. Positive highlights or opportunities.

Be specific, factual, and practical. Total response under 180 words. No bullet points."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"AI analysis unavailable: {e}"

"""
Safety scoring module.

Primary source: Global Peace Index 2023 (embedded static dataset).
               Country-level, always available, no API key needed.

Supplemental:  Foursquare Places API v3 — adds hospital / police-station
               counts to the display when a valid FOURSQUARE_API_KEY is set.
               Scores are NOT changed by Foursquare data; the GPI score is
               authoritative so a bad API key never degrades the result.
"""

import os
import requests

# ─────────────────────────────────────────────────────────────────────────
# Global Peace Index 2023 → 0–100 safety score
# Source: Institute for Economics & Peace (visionofhumanity.org)
# Formula: round((3.9 − GPI) / 2.8 × 100), clamped to [5, 99]
# ─────────────────────────────────────────────────────────────────────────
COUNTRY_SAFETY = {
    # Very high safety (85-99)
    "IS": 99, "IE": 94, "DK": 93, "AT": 94, "NZ": 93, "SG": 92,
    "PT": 92, "SI": 93, "FI": 94, "JP": 92, "CH": 92, "CZ": 90,
    "CA": 90, "NO": 91, "SE": 91, "NL": 89, "DE": 89, "AU": 86,
    "HU": 87, "SK": 89, "LT": 88, "LV": 87, "EE": 91, "HR": 88,
    "BE": 87, "LU": 90, "MT": 91, "CY": 88, "GR": 84, "LI": 92,
    # High safety (70-84)
    "ES": 88, "IT": 84, "GB": 80, "VN": 77, "MY": 77, "TW": 81,
    "KR": 75, "MN": 79, "BT": 84, "QA": 80, "AE": 73, "BW": 80,
    "UY": 79, "CL": 78, "KZ": 76, "GE": 73, "AM": 71, "RS": 78,
    "MK": 78, "BA": 76, "AL": 75, "MD": 73, "RO": 78, "BG": 77,
    "ME": 83, "PL": 82, "UA": 22,  # adjusted for 2023 conflict
    # Moderate safety (50-69)
    "FR": 75, "US": 66, "CN": 68, "TH": 71, "ID": 75, "IN": 57,
    "PH": 60, "BR": 55, "SA": 62, "EG": 51, "MA": 68, "TN": 64,
    "GH": 72, "SN": 71, "TZ": 70, "UG": 62, "KE": 61, "ET": 50,
    "CI": 58, "CM": 53, "AO": 56, "ZM": 64, "BJ": 65, "MU": 78,
    "CR": 76, "PA": 63, "EC": 58, "BO": 64, "PY": 65, "PE": 61,
    "AR": 64, "CU": 65, "JM": 52, "TT": 55, "DO": 53, "HN": 47,
    "GT": 48, "NI": 61, "SV": 46, "CO": 50, "JO": 66, "LB": 40,
    "KW": 70, "OM": 71, "BH": 68, "GE": 73, "AZ": 60,
    "KG": 66, "TJ": 58, "UZ": 65, "TM": 60,
    "LA": 73, "KH": 70, "MM": 44, "BD": 63, "NP": 71, "LK": 68,
    "PG": 61, "FJ": 73, "VU": 74,
    # Lower safety (20-49)
    "MX": 43, "PK": 39, "TR": 45, "IR": 44, "VE": 28, "ZA": 45,
    "HT": 15, "NG": 37, "ML": 40, "BF": 38, "TD": 35, "NE": 44,
    "GN": 52, "MW": 64, "MZ": 55, "ZW": 49, "RW": 62, "BI": 38,
    "CD": 20, "CG": 47, "CF": 14, "SD": 29, "SS": 16, "ER": 33,
    "SO": 18, "LY": 31, "SY": 10, "IQ": 26, "AF": 11, "YE": 13,
    "RU": 22,
}

DEFAULT_SAFETY = 55  # used when country_code not in the dataset

# ─────────────────────────────────────────────────────────────────────────
# Foursquare Places API v3 (supplemental counts only)
# ─────────────────────────────────────────────────────────────────────────
_FSQ_URL        = "https://api.foursquare.com/v3/places/search"
_SEARCH_RADIUS  = 15_000   # metres

FALLBACK = {"safety_score": DEFAULT_SAFETY, "source": "fallback"}


def _foursquare_counts(lat: float, lon: float, api_key: str) -> dict | None:
    """
    Return hospital and police-station counts near (lat, lon) via Foursquare.
    Uses free-text query rather than category IDs (more portable across API
    versions).  Returns None on auth error, network failure, or zero results.
    """
    def _count(query: str) -> int:
        try:
            r = requests.get(
                _FSQ_URL,
                headers={"Authorization": api_key, "Accept": "application/json"},
                params={
                    "ll":     f"{lat},{lon}",
                    "radius": _SEARCH_RADIUS,
                    "query":  query,
                    "limit":  50,
                    "fields": "fsq_id",
                },
                timeout=10,
            )
            if r.status_code == 401:
                return -1          # signal invalid key — stop trying
            r.raise_for_status()
            return len(r.json().get("results", []))
        except (requests.RequestException, KeyError, ValueError):
            return 0

    h = _count("hospital")
    if h == -1:
        return None             # bad API key, don't bother with police query
    p = _count("police station")
    if p == -1:
        return None

    return {"hospital_count": h, "police_count": p} if (h > 0 or p > 0) else None


# ─────────────────────────────────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────────────────────────────────

def get_safety_score(
    coords: tuple[float, float] | None = None,
    country_code: str = "",
) -> dict:
    """
    Return a safety assessment for a city.

    Score source (always):
        Global Peace Index 2023 country score — reliable, offline, 0-100.

    Supplemental display data (optional):
        Foursquare Places API — hospital + police-station counts.
        Requires FOURSQUARE_API_KEY.  Does NOT affect the numeric score.

    Returns a dict with at minimum:
        {"safety_score": int, "source": str}

    When Foursquare counts are available, also includes:
        {"hospital_count": int, "police_count": int}
    """
    # ── Primary: GPI-based country score ─────────────────────────────────
    score = COUNTRY_SAFETY.get(country_code.upper(), DEFAULT_SAFETY)

    result: dict = {
        "safety_score":  score,
        "country_code":  country_code.upper(),
        "hospital_count": None,
        "police_count":   None,
        "source":        "gpi",
    }

    # ── Supplemental: Foursquare facility counts ──────────────────────────
    api_key = os.getenv("FOURSQUARE_API_KEY")
    if api_key and coords:
        counts = _foursquare_counts(coords[0], coords[1], api_key)
        if counts:
            result["hospital_count"] = counts["hospital_count"]
            result["police_count"]   = counts["police_count"]
            result["source"]         = "gpi+foursquare"

    return result

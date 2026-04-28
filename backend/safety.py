import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


HEADERS = {"User-Agent": "GlobalEventRiskTracker/1.0"}

# Returned when either API is unavailable neutral score so the overall
# Travel Readiness Score isn't torpedoed by a single API outage.
FALLBACK = {"hospital_count": 0, "police_count": 0, "safety_score": 50}


def _get_bounding_box(city: str) -> tuple[str, str, str, str] | None:
    """
    Return the (south, west, north, east) bounding box for a city via Nominatim.
    Overpass uses this box to scope its geographic search.
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
        #Nominatim returns [south, north, west, east]; Overpass wants (s, w, n, e).
        s, n, w, e = results[0]["boundingbox"]
        return s, w, n, e
    except (requests.RequestException, KeyError, ValueError):
        return None


def _count_amenity(bbox: tuple[str, str, str, str], amenity: str) -> int:
    """
    Count how many nodes + ways of a given OSM amenity tag exist inside a bounding box.

    Uses Overpass `out count` so the API returns a single integer rather than
    transferring every matching geometry — fast and lightweight.
    """
    s, w, n, e = bbox
    query = f"""
    [out:json][timeout:25];
    (
      node[amenity={amenity}]({s},{w},{n},{e});
      way[amenity={amenity}]({s},{w},{n},{e});
    );
    out count;
    """
    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=30)
        response.raise_for_status()
        tags = response.json()["elements"][0]["tags"]
        return int(tags.get("total", 0))
    except (requests.RequestException, KeyError, ValueError, IndexError):
        return 0


def _compute_score(hospital_count: int, police_count: int) -> int:
    """
    Derive a safety score (0-100) from facility counts.

    Weights:
        Base score:     20  (every city gets a floor)
        Hospitals:  up to 50  (capped at ~17 facilities for full points)
        Police:     up to 30  (capped at ~15 facilities for full points)

    Examples:
        2 hospitals, 5 police  →  20 + 6 + 10  = 36  (small / underserved city)
        10 hospitals, 15 police → 20 + 30 + 30 = 80  (well-equipped city)
        17+ hospitals, 15+ police → 100            (major metro)
    """
    hospital_score = min(50, hospital_count * 3)
    police_score = min(30, police_count * 2)
    return min(100, 20 + hospital_score + police_score)


def get_safety_score(city: str) -> dict:
    """
    Count hospitals and police stations in a city using OpenStreetMap data
    (via the Overpass API) and convert the counts into a safety score.

    No API key required — both Nominatim and Overpass are free public services.

    Returns:
        {
            "hospital_count": int — number of OSM-tagged hospitals found,
            "police_count":   int — number of OSM-tagged police stations found,
            "safety_score":   int — score 0-100 (higher = safer / better served),
        }
        Falls back to {"hospital_count": 0, "police_count": 0, "safety_score": 50}
        if geocoding or the Overpass query fails.
    """
    bbox = _get_bounding_box(city)
    if bbox is None:
        return FALLBACK

    hospital_count = _count_amenity(bbox, "hospital")
    police_count = _count_amenity(bbox, "police")

    return {
        "hospital_count": hospital_count,
        "police_count": police_count,
        "safety_score": _compute_score(hospital_count, police_count),
    }

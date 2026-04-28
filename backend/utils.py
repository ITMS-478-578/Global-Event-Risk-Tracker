import os
from datetime import datetime


def load_api_key(env_var: str) -> str:
    """
    Read an API key from an environment variable.

    Raises EnvironmentError if the variable is not set, so misconfiguration
    is caught early rather than failing silently at request time.
    """
    pass


def format_timestamp(iso_string: str) -> str:
    """
    Convert an ISO 8601 timestamp string (e.g. "2024-06-01T14:30:00Z")
    into a human-readable format (e.g. "June 1, 2024 at 2:30 PM").

    Returns the original string unchanged if parsing fails.
    """
    pass


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a numeric value to [min_val, max_val].

    Useful for keeping partial scores within their expected range before
    they are summed into the final Travel Readiness Score.
    """
    pass

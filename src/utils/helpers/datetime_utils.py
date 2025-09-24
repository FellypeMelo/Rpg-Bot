from datetime import datetime, timezone
from typing import Optional, Any

def safe_parse_datetime(value: Any) -> Optional[datetime]:
    """Parse a value into a datetime if possible.

    - If value is already a datetime, return it.
    - If value is a string, attempt to parse with fromisoformat and return result or None.
    - Otherwise return None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None
    return None

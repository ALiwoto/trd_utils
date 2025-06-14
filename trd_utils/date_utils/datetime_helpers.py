



from datetime import datetime, timezone


def dt_from_ts(timestamp: float) -> datetime:
    """
    Return a datetime from a timestamp.
    :param timestamp: timestamp in seconds or milliseconds
    """
    if timestamp > 1e10:
        # Timezone in ms - convert to seconds
        timestamp /= 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def dt_to_ts(dt: datetime, default: int = 0) -> int:
    """
    Return dt in ms as a timestamp in UTC.
    If dt is None, return the given default.
    """
    if dt:
        return int(dt.timestamp() * 1000)
    return default

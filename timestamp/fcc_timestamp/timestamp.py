import json
from datetime import datetime, timezone, timedelta

from dateutil.parser import isoparse


def generate_response_from_date_string(dtstr: str):
    try:
        dt = _parse_datetime(dtstr)
        dt = dt.replace(tzinfo=timezone(timedelta(0), "GMT"))
        return _response_from_datetime(dt)
    except ValueError:
        return json.dumps({"error": "Invalid Date"})


def _parse_datetime(dtstr: str):
    if not dtstr:
        return datetime.utcnow()
    try:
        return isoparse(dtstr)
    except ValueError:
        pass
    try:
        timestamp = int(dtstr)
        return datetime.utcfromtimestamp(timestamp / 1000)
    except ValueError:
        pass
    raise ValueError


def _response_from_datetime(dt):
    return json.dumps(
        {
            "unix": int(dt.timestamp() * 1000),
            "utc": dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
        }
    )

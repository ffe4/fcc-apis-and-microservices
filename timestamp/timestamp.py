import json
from datetime import datetime, timezone, timedelta

from dateutil.parser import isoparse


def generate_response(dtstr: str):
    if not dtstr:
        return _response_from_datetime(datetime.utcnow())
    try:
        return _response_from_datetime(isoparse(dtstr))
    except ValueError:
        pass
    try:
        return _response_from_datetime(datetime.utcfromtimestamp(int(dtstr) / 1000))
    except ValueError:
        return json.dumps({"error": "Invalid Date"})


def _response_from_datetime(dt, tzinfo=timezone(timedelta(0), "GMT")):
    dt = dt.replace(tzinfo=tzinfo)
    return json.dumps(
        {
            "unix": int(dt.timestamp()) * 1000,
            "utc": dt.strftime("%a, %d %b %Y %H:%M:%S %Z"),
        }
    )

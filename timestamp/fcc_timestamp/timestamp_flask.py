from datetime import timezone, timedelta, datetime

from dateutil.parser import isoparse
from flask import Flask, jsonify

app = Flask(__name__)


def parse_date_string(data_string):
    if not data_string:
        return datetime.utcnow()
    try:
        return isoparse(data_string)
    except ValueError:
        pass
    try:
        timestamp = int(data_string)
        return datetime.utcfromtimestamp(timestamp / 1000)
    except ValueError:
        pass
    raise ValueError


@app.route("/")
@app.route("/<string:date_string>")
def get_time(date_string=""):
    try:
        dt = parse_date_string(date_string)
    except ValueError:
        return jsonify({"error": "Invalid Date"})
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(0), "GMT"))

    return jsonify(unix=int(dt.timestamp() * 1000), utc=dt)


if __name__ == "__main__":
    app.run()

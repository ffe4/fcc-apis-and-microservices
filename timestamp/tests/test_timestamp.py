import json
from datetime import datetime
from unittest.mock import patch

import pytest
from fcc_timestamp import timestamp_flask


@pytest.fixture
def client():
    timestamp_flask.app.config["TESTING"] = True
    with timestamp_flask.app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "date_string,expected",
    [
        (
            "1451001600000",
            {"unix": 1451001600000, "utc": "Fri, 25 Dec 2015 00:00:00 GMT"},
        ),
        ("2015-12-25", {"unix": 1451001600000, "utc": "Fri, 25 Dec 2015 00:00:00 GMT"}),
        ("invalid-date-string", {"error": "Invalid Date"}),
    ],
)
def test_generates_correct_response_from_datestring(client, date_string, expected):
    response = client.get(date_string)
    actual = json.loads(response.data)
    assert actual == expected


def test_responds_with_current_time_without_date_string(client):
    expected = {"unix": 947073890000, "utc": "Wed, 05 Jan 2000 12:04:50 GMT"}
    with patch("fcc_timestamp.timestamp_flask.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = datetime(2000, 1, 5, 12, 4, 50)
        response = client.get()
        actual = json.loads(response.data)
    assert actual == expected


def test_returns_identical_timestamp(client):
    timestamp = 947073890012
    expected = {"unix": timestamp, "utc": "Wed, 05 Jan 2000 12:04:50 GMT"}
    response = client.get(str(timestamp))
    actual = json.loads(response.data)
    assert actual == expected

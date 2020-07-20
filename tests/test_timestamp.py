import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from timestamp.timestamp import generate_response


@pytest.mark.parametrize(
    "datestring,expected",
    [
        (
            "1451001600000",
            {"unix": 1451001600000, "utc": "Fri, 25 Dec 2015 00:00:00 GMT"},
        ),
        ("2015-12-25", {"unix": 1451001600000, "utc": "Fri, 25 Dec 2015 00:00:00 GMT"}),
        ("invalid-date-string", {"error": "Invalid Date"}),
    ],
)
def test_generates_correct_response_from_datestring(datestring, expected):
    actual = generate_response(datestring)
    assert actual == json.dumps(expected)


def test_generates_correct_response_without_input():
    expected = json.dumps(
        {"unix": 947073890000, "utc": "Wed, 05 Jan 2000 12:04:50 GMT"}
    )
    with patch("timestamp.timestamp.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = datetime(2000, 1, 5, 12, 4, 50)
        actual = generate_response("")
    assert actual == expected

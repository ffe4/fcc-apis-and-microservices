import json
from werkzeug.datastructures import Headers

from fcc_request_header_parser import generate_response


def test_generates_correct_response():
    agent = "Mozilla/5.0"
    language = "en-US,en;q=0.5"
    ip = "159.20.14.100"
    expected = json.dumps({"ipaddress": ip, "language": language, "software": agent,})
    test_headers = Headers()
    test_headers.add("Content-Type", "text/plain")
    test_headers.add("User-Agent", agent)
    test_headers.add("Accept-Language", language)

    actual = generate_response(test_headers, ip)
    assert actual == expected

    test_headers.add("X-Forwarded-For", ip)

    actual = generate_response(test_headers, "no-ip")
    assert actual == expected

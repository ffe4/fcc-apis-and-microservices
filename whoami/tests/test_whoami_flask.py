import json

import pytest

from fcc_whoami import whoami_flask


@pytest.fixture
def client():
    whoami_flask.app.config["TESTING"] = True
    with whoami_flask.app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "ip,agent,language", [("127.0.0.1", "Mozilla/5.0", "en-US,en")]
)
def test_empty_db(client, ip, agent, language):
    expected = {"ipaddress": ip, "language": language, "software": agent}

    response = client.get(
        "/",
        headers={
            "X-Forwarded-For": ip,
            "User-Agent": agent,
            "Accept-Language": language,
        },
    )
    actual = json.loads(response.data)
    assert actual == expected

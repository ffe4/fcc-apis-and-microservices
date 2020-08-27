import json
from unittest.mock import patch

import fakeredis
import pytest

from fcc_shorturl import shorturl_flask, RedisShortenedStorage


class FakeRedisShortenedStorage(RedisShortenedStorage):
    def __init__(self):
        with patch(
            "fcc_shorturl.redis_shortened_storage.redis.Redis",
            fakeredis.FakeStrictRedis,
        ):
            super().__init__("", "", "", int_to_str_func=str)

    def load_test_data(self, test_data):
        for k, v in test_data["long_url_key"].items():
            self._redis.set(self.prefix_long + k, v)
        for k, v in test_data["short_url_key"].items():
            self._redis.set(self.prefix_short + k, v)


TEST_DATA = {
    "long_url_key": {
        "http://google.com": "1",
        "http://redis.com": "2",
        "https://flask.palletsprojects.com/": "3",
    },
    "short_url_key": {
        "1": "http://google.com",
        "2": "http://redis.com",
        "3": "https://flask.palletsprojects.com/",
    },
}


@pytest.fixture
def client():
    shorturl_flask.app.config["TESTING"] = True
    with patch(
        "fcc_shorturl.shorturl_flask.redis", FakeRedisShortenedStorage()
    ) as fake_redis, shorturl_flask.app.test_client() as client:
        fake_redis.load_test_data(TEST_DATA)
        yield client


@pytest.mark.parametrize(
    "long_url,expected_url",
    [("google.com", "http://google.com"), ("http://redis.com", "http://redis.com")],
)
def test_saves_normalized_urls(client, long_url, expected_url):
    response = client.post("/new", data=dict(url=long_url))
    actual = json.loads(response.data)["original_url"]
    assert actual == expected_url


@pytest.mark.parametrize("short_url_key,target", TEST_DATA["short_url_key"].items())
def test_returns_redirect_to_long_url(client, short_url_key, target):
    response = client.get("/" + short_url_key.split(":")[-1])
    assert response.status == "301 MOVED PERMANENTLY"
    assert response.headers["Location"] == target

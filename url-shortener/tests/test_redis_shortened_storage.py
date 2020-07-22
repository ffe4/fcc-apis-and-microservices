from unittest.mock import patch

import fakeredis
from fcc_url_shortener import RedisShortenedStorage


@patch("fcc_url_shortener.redis_shortened_storage.redis.Redis", fakeredis.FakeStrictRedis)
def test_adds_and_gets_shortened_entries():
    redis_store = RedisShortenedStorage("", "", "", int_to_str_func=str)
    short = redis_store.add("test")
    long = redis_store.get(short)
    assert long == "test"
    assert short == "1"


@patch("fcc_url_shortener.redis_shortened_storage.redis.Redis", fakeredis.FakeStrictRedis)
def test_add_returns_consecutive_ids():
    redis_store = RedisShortenedStorage("", "", "", int_to_str_func=str)
    for i in range(1, 10):
        redis_store.add(str(i))
    for i in range(1, 10):
        assert redis_store.get(str(i)) == str(i)


@patch("fcc_url_shortener.redis_shortened_storage.redis.Redis", fakeredis.FakeStrictRedis)
def test_adding_existent_url_does_not_overwrite_old_uid():
    redis_store = RedisShortenedStorage("", "", "", int_to_str_func=str)
    short1 = redis_store.add("test")
    for i in range(1, 15):
        redis_store.add(f"test-{i}")
    short2 = redis_store.add("test")
    assert short1 == short2


@patch("fcc_url_shortener.redis_shortened_storage.redis.Redis", fakeredis.FakeStrictRedis)
def test_incomplete_add_gets_fixed_after_new_add():
    prefix_short = "short:"
    prefix_long = "long:"
    redis_store = RedisShortenedStorage("", "", "", prefix_short, prefix_long, str)

    short = redis_store.add("test")
    assert redis_store._redis.get(prefix_short + short) is not None
    redis_store._redis.delete(prefix_short + short)
    assert redis_store._redis.get(prefix_short + short) is None
    redis_store.add("test")
    assert redis_store._redis.get(prefix_short + short) == "test"


@patch("fcc_url_shortener.redis_shortened_storage.redis.Redis", fakeredis.FakeStrictRedis)
def test_key_prefix_is_applied_properly():
    prefix_short = "short:"
    prefix_long = "long:"
    redis_store = RedisShortenedStorage("", "", "", prefix_short, prefix_long, str)
    long = "test"
    short = redis_store.add(long)
    assert redis_store.get(short) == long
    assert redis_store.get(prefix_short + short) is None
    assert redis_store._redis.get(short) is None
    assert redis_store._redis.get(prefix_short + short) == long
    assert redis_store._redis.get(long) is None
    assert redis_store._redis.get(prefix_long + long) == short

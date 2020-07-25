from typing import Union

import redis


ID_COUNTER = "short-counter"


def _base34(num: int) -> str:
    alphabet = "123456789abcdefghijkmnopqrstuvwxyz"
    base_string = ""
    while num:
        num, d = divmod(num, 34)
        base_string += alphabet[d]
    if len(base_string) == 0:
        base_string += alphabet[0]
    return base_string


class RedisShortenedStorage:
    def __init__(
        self,
        host,
        port,
        password,
        prefix_short="short_url:",
        prefix_long="long_url:",
        int_to_str_func=_base34,
    ):
        self.int_to_str = int_to_str_func
        self.prefix_long = prefix_long
        self.prefix_short = prefix_short
        self._redis = redis.Redis(
            host=host, port=port, password=password, decode_responses=True
        )

    def _generate_uid(self):
        id_counter = self._redis.incr(ID_COUNTER)
        return self.int_to_str(id_counter)

    def get(self, key) -> Union[str, None]:
        return self._redis.get(self.prefix_short + key)

    def add(self, long) -> str:
        short = self._generate_uid()
        if self._redis.setnx(self.prefix_long + long, short):
            self._redis.set(self.prefix_short + short, long)
            return short
        # `long` was already in database. In case the original addition
        # failed before `set(short, long)` was called we rectify that here.
        short = self._redis.get(self.prefix_long + long) or short
        self._redis.setnx(self.prefix_short + short, long)
        return short

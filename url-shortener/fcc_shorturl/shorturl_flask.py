import os
from socket import gethostbyname, gaierror
from urllib.parse import urlparse, urlunparse

from flask import Flask, request, redirect, abort, jsonify
from fcc_shorturl import RedisShortenedStorage

app = Flask(__name__)

try:
    app.config.from_pyfile("/etc/config/redis-connection.cfg")  # TODO use ENV
except FileNotFoundError:
    pass


redis = RedisShortenedStorage(
    app.config.get("REDIS_HOST") or os.getenv("REDIS_HOST") or "localhost",
    app.config.get("REDIS_PORT") or os.getenv("REDIS_PORT") or 6379,
    os.getenv("REDIS_PASSWORD"),  # TODO manage secrect with Vault
)


def parse_user_url(url):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if not scheme:
        scheme = "http"
    if not netloc:
        netloc, path = path, netloc
    return urlunparse((scheme, netloc, path, params, query, fragment))


def _is_valid_url(url):
    # checks validity by performing a dns lookup
    _, netloc, *_ = urlparse(url)
    try:
        gethostbyname(netloc)
        return True
    except gaierror:
        return False


@app.route("/new", methods=["POST"])
def add_url():
    url = request.form.get("url")
    url = parse_user_url(url)
    if not _is_valid_url(url):
        return jsonify({"error": "invalid URL"})
    short_url = redis.add(url)
    return jsonify({"original_url": url, "short_url": short_url})


@app.route("/<short_url>", methods=["GET"])
def get_url(short_url):
    long_url = redis.get(short_url)
    if long_url is None:
        abort(404)
    response = redirect(long_url, code=301)
    response.headers["Cache-Control"] = "max-age=15"
    return response


if __name__ == "__main__":
    app.run()

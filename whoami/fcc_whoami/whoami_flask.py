from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify(
        # TODO proxy awareness
        ipaddress=request.headers.get("X-Forwarded-For") or request.remote_addr,
        language=request.headers.get("Accept-Language"),
        software=request.headers.get("User-Agent"),
    )


if __name__ == "__main__":
    app.run()

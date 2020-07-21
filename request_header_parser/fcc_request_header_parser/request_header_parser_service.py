from flask import Flask, request
from fcc_request_header_parser import generate_response

app = Flask(__name__)


@app.route("/")
def hello_world():
    return generate_response(request.headers, request.remote_addr)


if __name__ == "__main__":
    app.run()

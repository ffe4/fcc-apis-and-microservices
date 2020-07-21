from flask import Flask
from fcc_timestamp import generate_response_from_date_string

app = Flask(__name__)


@app.route("/")
@app.route("/<string:dtstr>")
def hello_world(dtstr=""):
    return generate_response_from_date_string(dtstr)


if __name__ == "__main__":
    app.run()

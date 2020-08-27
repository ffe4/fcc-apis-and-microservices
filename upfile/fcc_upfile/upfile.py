from flask import Flask, request, abort, jsonify

app = Flask(__name__)


@app.route("/", methods=["POST"])
def upfile():
    if not (file := request.files.get("upfile")):
        abort(400, "missing `upfile` file parameter")
    return jsonify(
        name=file.filename,
        size=len(file.read()),
    )


if __name__ == '__main__':
    app.run()

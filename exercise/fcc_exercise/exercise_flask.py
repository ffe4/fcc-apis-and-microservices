import os

from flask import Flask
from flask_cors import CORS

from fcc_exercise.database import db
from fcc_exercise.views import exercise_api


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    app.config.from_mapping(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI") or "sqlite:///:memory:",
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(exercise_api)

    return app


app = create_app()


if __name__ == "__main__":
    db.init_db()
    app.run()

from datetime import datetime

from dateutil.parser import parse
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    _id = db.synonym("id")
    username = db.synonym("name")

    exercises = db.relationship("Exercise", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    _id = db.synonym("id")

    user = db.relationship("User", back_populates="exercises")


@app.route("/new-user", methods=["POST"])
def create_user():
    username = request.data.decode("utf-8")
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({"_id": user.id, "username": user.name,})


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"_id": user.id, "username": user.name} for user in users])


@app.route("/add", methods=["POST"])
def add_exercise():
    if not all(key in request.form for key in ("userId", "description", "duration")):
        abort(400, "missing field")
    data = {
        "user_id": request.form["userId"],
        "description": request.form["description"],
        "duration": request.form["duration"]
    }
    if request.form.get("date"):
        try:
            dt = parse(request.form["date"])
        except:
            abort(400, "unsupported date format")
        data["date"] = dt
    exercise = Exercise(**data)
    user = User.query.get(exercise.user_id)
    db.session.add(exercise)
    db.session.commit()
    return jsonify({
        "_id": user.id,
        "username": user.name,
        "date": datetime.isoformat(exercise.date),
        "duration": exercise.duration,
        "description": exercise.description,
    })


@app.route("/log", methods=["GET"])
def exercise_log():
    user_id = request.args.get("userId")
    if user_id is None:
        abort(400, "missing mandatory userId argument")
    user = User.query.get(user_id)
    query = db.session.query(Exercise).filter_by(user_id=user.id)
    if request.args.get("from") and request.args.get("to"):
        try:
            from_date = parse(request.args.get("from"))
            to_date = parse(request.args.get("to"))
        except:
            pass
        else:
            query = query.filter(Exercise.date >= from_date)
            query = query.filter(Exercise.date <= to_date)
    if request.args.get("limit"):
        query = query.limit(request.args.get("limit"))
    exercises = query.all()
    return jsonify({
        "_id": user.id,
        "username": user.name,
        "count": len(exercises),
        "log": [
            {
                "description": ex.description,
                "duration": ex.duration,
                "date": ex.date,
            } for ex in exercises
        ]
    })


def init_db():
    db.create_all()


def reset_db():
    if not app.config["TESTING"]:
        raise Exception("This operations is only permitted in a test environment")
    db.session.remove()
    db.drop_all()


if __name__ == "__main__":
    init_db()
    app.run()

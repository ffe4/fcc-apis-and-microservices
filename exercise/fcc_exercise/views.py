from datetime import datetime

from dateutil.parser import parse
from flask import Blueprint, request, jsonify, abort

from fcc_exercise.models import db, User, Exercise


exercise_api = Blueprint("exercise_api", __name__)


@exercise_api.route("/new-user", methods=["POST"])
def create_user():
    username = request.data.decode("utf-8")
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({"_id": user.id, "username": user.name, })


@exercise_api.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"_id": user.id, "username": user.name} for user in users])


@exercise_api.route("/add", methods=["POST"])
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
    if user is None:
        abort(400, "user not found")
    db.session.add(exercise)
    db.session.commit()
    return jsonify({
        "_id": user.id,
        "username": user.name,
        "date": datetime.isoformat(exercise.date),
        "duration": exercise.duration,
        "description": exercise.description,
    })


@exercise_api.route("/log", methods=["GET"])
def exercise_log():
    user_id = request.args.get("userId")
    if user_id is None:
        abort(400, "missing mandatory userId argument")
    user = User.query.get(user_id)
    if user is None:
        abort(400, "user not found")
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
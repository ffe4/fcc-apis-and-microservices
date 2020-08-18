from flask import Flask, request, jsonify
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

from fcc_exercise.database import db


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

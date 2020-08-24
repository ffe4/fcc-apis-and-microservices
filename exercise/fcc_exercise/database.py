import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def reset_db():
    db.session.remove()
    db.drop_all()


@click.command("init-db")
@with_appcontext
def init_db_cmd():
    db.create_all()

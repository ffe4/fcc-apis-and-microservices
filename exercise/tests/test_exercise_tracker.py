import json
from datetime import datetime

import pytest
from pytest_bdd import given, when, then, parsers, scenarios

from fcc_exercise import exercise_flask


scenarios("exercise_tracker.feature")


@pytest.fixture
def context():
    return {}


@pytest.fixture
def client():
    exercise_flask.app.config["DATABASE_URI"] = "sqlite:///:memory:"
    exercise_flask.app.config["TESTING"] = True

    with exercise_flask.app.test_client() as client:
        with exercise_flask.app.app_context():
            exercise_flask.init_db()
        yield client

    exercise_flask.reset_db()
    exercise_flask.init_db()


@given("the API endpoint /api/exercise")
def api_endpoint(client):
    return client


@when(parsers.parse("I send a POST request with form data {username:w} to /new-user"))
def new_user(api_endpoint, username, context):
    response = api_endpoint.post("/new-user", data=username)
    context["response"] = response.get_json()


@then(
    parsers.parse(
        "a {model_name:w} with {field:w} {field_value:w} should exist in the database"
    )
)
def row_exists(model_name: str, field: str, field_value):
    model = getattr(exercise_flask, model_name.title())
    result = model.query.filter_by(username=field_value).first()
    assert result


@then(parsers.parse("the username and _id of {username:w} will be returned"))
def user_returned(context, username):
    actual = context["response"]
    assert actual
    assert actual["username"] == username
    assert isinstance(actual["_id"], int)


def test_users_route_returns_list_of_created_users(client):
    users = {"UserA", "UserB", "@User", "user C", "/.,;'"}
    for name in users:
        client.post("/new-user", data=name)

    response = client.get("/users")
    data = json.loads(response.data)

    assert set([user['username'] for user in data]) == users


def test_add_route_creates_exercise_entry(client):
    test_user = exercise_flask.User(username="Alex")
    exercise_flask.db.session.add(test_user)
    exercise_flask.db.session.commit()
    exercise = {
        "userId": test_user.id,
        "description": "fast typing",
        "duration": 10,
        "date": datetime(2020, 10, 10).isoformat(),
    }

    client.post("/add", data=exercise)

    actual = exercise_flask.Exercise.query.first()
    assert actual is not None
    assert actual.user_id == exercise["userId"]
    assert actual.description == exercise["description"]
    assert actual.duration == exercise["duration"]
    assert actual.date == datetime.fromisoformat(exercise["date"])


def test_add_route_creates_date_if_none_specified(client):
    test_user = exercise_flask.User(username="Alex")
    exercise_flask.db.session.add(test_user)
    exercise_flask.db.session.commit()
    exercise = {
        "userId": test_user.id,
        "description": "fast typing",
        "duration": 10,
    }

    client.post("/add", data=exercise)

    actual = exercise_flask.Exercise.query.first()
    assert actual is not None
    assert actual.date is not None

import json
import string
from datetime import datetime
import random

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


def create_test_user(name=None):
    if name is None:
        name = ''.join(random.choices(string.ascii_uppercase, k=10))
    test_user = exercise_flask.User(username=name)
    exercise_flask.db.session.add(test_user)
    exercise_flask.db.session.commit()
    return test_user


def create_test_exercise(user_id, description=None, duration=None, date=None):
    description = description or ''.join(random.choices(string.ascii_uppercase, k=10))
    duration = duration or random.randint(10, 10000)
    date = date or datetime(2020, 1, random.randint(1, 10), random.randint(8, 20))
    exercise = exercise_flask.Exercise(
        user_id=user_id,
        description=description,
        duration=duration,
        date=date,
    )
    exercise_flask.db.session.add(exercise)
    exercise_flask.db.session.commit()
    return exercise


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
    test_user = create_test_user()
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
    test_user = create_test_user()
    exercise = {
        "userId": test_user.id,
        "description": "fast typing",
        "duration": 10,
    }

    client.post("/add", data=exercise)

    actual = exercise_flask.Exercise.query.first()
    assert actual is not None
    assert actual.date is not None


def test_add_route_returns_user_and_exercise_fields_in_response(client):
    test_user = create_test_user()
    exercise = {
        "userId": test_user.id,
        "description": "fast typing",
        "duration": 10,
        "date": datetime(2020, 10, 10).isoformat(),
    }

    response = client.post("/add", data=exercise)
    actual = json.loads(response.data)

    assert actual["_id"] == test_user.id
    assert actual["username"] == test_user.name
    assert actual["description"] == exercise["description"]
    assert actual["duration"] == exercise["duration"]
    assert actual["date"] == exercise["date"]


def test_log_route_returns_empty_exercise_log_for_new_user(client):
    test_user = create_test_user()

    response = client.get(f"/log?userId={test_user.id}")
    actual = json.loads(response.data)

    assert actual["_id"] == test_user.id
    assert actual["username"] == test_user.name
    assert actual["count"] == 0
    assert actual["log"] == []


def test_log_route_returns_exercise_log_for_given_user(client):
    _ = create_test_user()
    test_user = create_test_user()

    exercises = [create_test_exercise(test_user.id) for _ in range(5)]

    response = client.get(f"/log?userId={test_user.id}")
    actual = json.loads(response.data)

    assert actual["_id"] == test_user.id
    assert actual["username"] == test_user.name
    assert actual["count"] == len(exercises)
    assert len(actual["log"]) == len(exercises)
    assert set(ex["description"] for ex in actual["log"]) == set(ex.description for ex in exercises)
    assert set(ex["duration"] for ex in actual["log"]) == set(ex.duration for ex in exercises)
    assert set(ex["date"] for ex in actual["log"]) == set(ex.date.strftime('%a, %d %b %Y %H:%M:%S GMT') for ex in exercises)


def test_limit_argument_limits_exercise_log_results(client):
    test_user = create_test_user()
    for i in range(25):
        create_test_exercise(test_user.id)

    response = client.get(f"/log?userId={test_user.id}")
    actual_full = json.loads(response.data)
    response = client.get(f"/log?userId={test_user.id}&limit=20")
    actual_limited = json.loads(response.data)

    assert len(actual_full["log"]) == 25
    assert len(actual_limited["log"]) == 20


def test_from_to_limiting_of_exercise_log_results(client):
    test_user = create_test_user()
    create_test_exercise(test_user.id, date=datetime(2020, 1, 1))
    create_test_exercise(test_user.id, date=datetime(2020, 1, 2))
    create_test_exercise(test_user.id, date=datetime(2020, 1, 3))
    create_test_exercise(test_user.id, date=datetime(2020, 1, 4))

    response = client.get(f"/log?userId={test_user.id}&from=2020-01-02&to=2020-01-03")
    actual = json.loads(response.data)

    assert len(actual["log"]) == 2


def test_missing_userid_field_results_in_code_400(client):
    response = client.get(f"/log")
    assert response.status_code == 400


def test_missing_add_route_field_results_in_code_400(client):
    response = client.post(f"/add", data={
        "userId": 1,
        "description": "test",
    })
    assert response.status_code == 400


def test_invalid_date_format_results_in_code_400(client):
    response = client.post(f"/add", data={
        "userId": 1,
        "description": "test",
        "duration": 100,
        "date": "test"
    })
    assert response.status_code == 400

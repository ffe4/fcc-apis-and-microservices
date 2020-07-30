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

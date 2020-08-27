from io import BytesIO

import pytest

from fcc_upfile import app


@pytest.fixture
def client():
    test_config = {
        "TESTING": True,
        "DEBUG": True
    }
    app.config.from_mapping(test_config)
    with app.test_client() as client:
        return client


def test_app_response_contains_filename_and_size(client):
    response = client.post("/", content_type="multipart/form-data", data=dict(
        upfile=(BytesIO(b"\xFF" * 42), 'filename.test')
    ))

    assert response.status_code == 200
    actual = response.get_json()
    assert actual
    assert actual["name"] == "filename.test"
    assert actual["size"] == 42


def test_status_400_if_no_upfile_parameter(client):
    response = client.post("/", content_type="multipart/form-data", data={})
    assert response.status_code == 400

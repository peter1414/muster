import pytest

from muster import create_app
from muster.extensions import db as _db


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, username="jdoe", email="jdoe@example.com", password="correcthorse"):
    return client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def auth_headers(client, **kwargs):
    resp = register(client, **kwargs)
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

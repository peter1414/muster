from tests.conftest import auth_headers, register


def test_register_success(client):
    resp = register(client)
    assert resp.status_code == 201
    body = resp.get_json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["username"] == "jdoe"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "abc", "email": "a@b.com", "password": "short"},
    )
    assert resp.status_code == 400


def test_register_rejects_bad_username(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "a b!", "email": "a@b.com", "password": "correcthorse"},
    )
    assert resp.status_code == 400


def test_register_duplicate_username_rejected(client):
    register(client)
    resp = register(client, email="other@example.com")
    assert resp.status_code == 409


def test_register_duplicate_email_rejected(client):
    register(client)
    resp = register(client, username="other")
    assert resp.status_code == 409


def test_login_success(client):
    register(client)
    resp = client.post(
        "/api/auth/login", json={"username": "jdoe", "password": "correcthorse"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    register(client)
    resp = client.post(
        "/api/auth/login", json={"username": "jdoe", "password": "wrongwrong"}
    )
    assert resp.status_code == 401


def test_login_unknown_user_same_status_as_wrong_password(client):
    resp = client.post(
        "/api/auth/login", json={"username": "nobody", "password": "wrongwrong"}
    )
    assert resp.status_code == 401


def test_refresh_token_issues_new_access_token(client):
    resp = register(client)
    refresh_token = resp.get_json()["refresh_token"]
    resp = client.post(
        "/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_me_requires_auth(client):
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client):
    headers = auth_headers(client)
    resp = client.get("/api/me", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "jdoe"


def test_forgot_password_does_not_leak_account_existence(client):
    register(client)
    resp_exists = client.post("/api/auth/forgot-password", json={"email": "jdoe@example.com"})
    resp_missing = client.post("/api/auth/forgot-password", json={"email": "nope@example.com"})
    assert resp_exists.status_code == 200
    assert resp_missing.status_code == 200
    assert resp_exists.get_json()["message"] == resp_missing.get_json()["message"]


def test_reset_password_flow(client):
    register(client)
    resp = client.post("/api/auth/forgot-password", json={"email": "jdoe@example.com"})
    token = resp.get_json()["dev_reset_token"]  # dev-mode token surfacing (no email configured)

    resp = client.post(
        "/api/auth/reset-password", json={"token": token, "password": "newpassword123"}
    )
    assert resp.status_code == 200

    # old password no longer works
    resp = client.post(
        "/api/auth/login", json={"username": "jdoe", "password": "correcthorse"}
    )
    assert resp.status_code == 401

    # new password works
    resp = client.post(
        "/api/auth/login", json={"username": "jdoe", "password": "newpassword123"}
    )
    assert resp.status_code == 200


def test_reset_password_rejects_bad_token(client):
    resp = client.post(
        "/api/auth/reset-password", json={"token": "garbage", "password": "newpassword123"}
    )
    assert resp.status_code == 400


def test_delete_account_removes_user_and_entries(client):
    headers = auth_headers(client)
    client.post(
        "/api/entries",
        json={"exercise": "pushups", "value": 60},
        headers=headers,
    )

    resp = client.delete("/api/auth/account", headers=headers)
    assert resp.status_code == 200

    # token is for a now-deleted user; /api/me should 404
    resp = client.get("/api/me", headers=headers)
    assert resp.status_code == 404

    # can register the same username again since it was actually deleted
    resp = register(client)
    assert resp.status_code == 201


def test_delete_account_requires_auth(client):
    resp = client.delete("/api/auth/account")
    assert resp.status_code == 401

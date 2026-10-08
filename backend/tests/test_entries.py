from tests.conftest import auth_headers


def test_create_entry_reps(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/entries",
        json={"exercise": "pushups", "value": 65, "notes": "felt good"},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["exercise"] == "pushups"
    assert body["value"] == 65
    assert body["display_value"] == 65
    assert body["notes"] == "felt good"


def test_create_entry_time_accepts_mmss_string(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/entries",
        json={"exercise": "run_1_5mi", "value": "9:45"},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["value"] == 585  # 9*60+45
    assert body["display_value"] == "9:45"


def test_create_entry_rejects_unknown_exercise(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/entries", json={"exercise": "bench_press", "value": 100}, headers=headers
    )
    assert resp.status_code == 400


def test_create_entry_rejects_negative_value(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/entries", json={"exercise": "pushups", "value": -5}, headers=headers
    )
    assert resp.status_code == 400


def test_create_entry_requires_auth(client):
    resp = client.post("/api/entries", json={"exercise": "pushups", "value": 50})
    assert resp.status_code == 401


def test_list_entries_paginates(client):
    headers = auth_headers(client)
    for i in range(25):
        client.post(
            "/api/entries", json={"exercise": "situps", "value": 60 + i}, headers=headers
        )

    resp = client.get("/api/entries?page=1&per_page=10", headers=headers)
    body = resp.get_json()
    assert resp.status_code == 200
    assert len(body["entries"]) == 10
    assert body["total"] == 25
    assert body["total_pages"] == 3
    assert body["has_next"] is True


def test_list_entries_filter_by_exercise(client):
    headers = auth_headers(client)
    client.post("/api/entries", json={"exercise": "pushups", "value": 60}, headers=headers)
    client.post("/api/entries", json={"exercise": "situps", "value": 70}, headers=headers)

    resp = client.get("/api/entries?exercise=pushups", headers=headers)
    body = resp.get_json()
    assert body["total"] == 1
    assert body["entries"][0]["exercise"] == "pushups"


def test_entries_are_scoped_to_owner(client):
    headers_a = auth_headers(client, username="alice", email="alice@example.com")
    resp = client.post(
        "/api/entries", json={"exercise": "pushups", "value": 60}, headers=headers_a
    )
    entry_id = resp.get_json()["id"]

    headers_b = auth_headers(client, username="bob", email="bob@example.com")
    # bob can't see alice's entry in his list
    resp = client.get("/api/entries", headers=headers_b)
    assert resp.get_json()["total"] == 0

    # bob can't edit or delete alice's entry
    resp = client.put(
        f"/api/entries/{entry_id}", json={"value": 99}, headers=headers_b
    )
    assert resp.status_code == 404

    resp = client.delete(f"/api/entries/{entry_id}", headers=headers_b)
    assert resp.status_code == 404


def test_update_entry(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/entries", json={"exercise": "pushups", "value": 60}, headers=headers
    )
    entry_id = resp.get_json()["id"]

    resp = client.put(
        f"/api/entries/{entry_id}",
        json={"value": 75, "notes": "PR"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["value"] == 75
    assert body["notes"] == "PR"
    assert body["exercise"] == "pushups"  # unspecified field preserved


def test_delete_entry(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/entries", json={"exercise": "pushups", "value": 60}, headers=headers
    )
    entry_id = resp.get_json()["id"]

    resp = client.delete(f"/api/entries/{entry_id}", headers=headers)
    assert resp.status_code == 200

    resp = client.get("/api/entries", headers=headers)
    assert resp.get_json()["total"] == 0


def test_dashboard_shows_latest_entry_and_tier(client):
    headers = auth_headers(client)
    client.post("/api/entries", json={"exercise": "pushups", "value": 40}, headers=headers)
    client.post("/api/entries", json={"exercise": "pushups", "value": 85}, headers=headers)

    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    pushups_card = next(c for c in body["cards"] if c["key"] == "pushups")
    assert pushups_card["entry"]["value"] == 85  # latest, not first
    assert pushups_card["tier"] == "competitive"  # 85 >= competitive(80), < max(100)
    assert body["total_entries"] == 2


def test_standards_endpoint_is_public(client):
    resp = client.get("/api/standards")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "pushups" in body["standards"]
    assert body["exercise_order"][0] == "pushups"

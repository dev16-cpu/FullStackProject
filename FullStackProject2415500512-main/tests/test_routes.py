"""Tests for general routes: home, students, form-demo, health, and error pages."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"FullStack" in resp.data


def test_students(client):
    resp = client.get("/students")
    assert resp.status_code == 200
    assert b"student" in resp.data.lower()


def test_form_demo_get(client):
    resp = client.get("/form-demo")
    assert resp.status_code == 200


def test_form_demo_valid_post(client):
    resp = client.post(
        "/form-demo",
        data={"name": "alice", "mobile": "1234567890", "password": "secret12"},
    )
    assert resp.status_code == 200
    assert b"alice" in resp.data


def test_form_demo_short_name(client):
    resp = client.post(
        "/form-demo",
        data={"name": "ab", "mobile": "1234567890", "password": "secret12"},
    )
    assert resp.status_code == 200
    assert b"5 characters" in resp.data


def test_form_demo_invalid_mobile(client):
    resp = client.post(
        "/form-demo",
        data={"name": "alice", "mobile": "123", "password": "secret12"},
    )
    assert resp.status_code == 200
    assert b"10 digits" in resp.data


def test_form_demo_short_password(client):
    resp = client.post(
        "/form-demo",
        data={"name": "alice", "mobile": "1234567890", "password": "x"},
    )
    assert resp.status_code == 200
    assert b"8 characters" in resp.data


def test_404_page(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert b"not found" in resp.data.lower()


def test_security_headers(client):
    resp = client.get("/")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

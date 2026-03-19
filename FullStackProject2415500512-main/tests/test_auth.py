"""Tests for auth routes: register, login, logout."""


def _register(client, username="testuser", email="test@example.com", password="Password1"):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def test_register_get(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200


def test_register_success(client):
    resp = _register(client)
    assert resp.status_code == 200
    assert b"Registration successful" in resp.data


def test_register_duplicate_username(client):
    _register(client)
    resp = _register(client)
    assert b"already exists" in resp.data


def test_register_duplicate_email(client):
    _register(client, username="user1", email="shared@example.com")
    resp = _register(client, username="user2", email="shared@example.com")
    assert b"already exists" in resp.data


def test_register_weak_password(client):
    resp = _register(client, password="short")
    assert resp.status_code == 200
    assert b"8 characters" in resp.data


def test_register_no_uppercase(client):
    resp = _register(client, password="password1")
    assert resp.status_code == 200
    assert b"uppercase" in resp.data


def test_register_no_digit(client):
    resp = _register(client, password="PasswordNoDigit")
    assert resp.status_code == 200
    assert b"digit" in resp.data


def test_login_get(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200


def test_login_success(client):
    _register(client)
    resp = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "Password1"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data


def test_login_invalid_password(client):
    _register(client)
    resp = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in resp.data


def test_login_unknown_user(client):
    resp = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "Password1"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in resp.data


def test_login_redirects_authenticated_user(client):
    _register(client)
    client.post("/auth/login", data={"username": "testuser", "password": "Password1"})
    resp = client.get("/auth/login", follow_redirects=True)
    assert resp.status_code == 200
    assert b"FullStack" in resp.data


def test_logout(client):
    _register(client)
    client.post("/auth/login", data={"username": "testuser", "password": "Password1"})
    resp = client.post("/auth/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"signed out" in resp.data


def test_register_redirects_authenticated_user(client):
    _register(client)
    client.post("/auth/login", data={"username": "testuser", "password": "Password1"})
    resp = client.get("/auth/register", follow_redirects=True)
    assert resp.status_code == 200
    assert b"FullStack" in resp.data

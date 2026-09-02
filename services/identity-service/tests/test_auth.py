def test_register_and_login(client):
    resp = client.post("/auth/register", json={
        "email": "attendee@example.com",
        "full_name": "Ada Attendee",
        "password": "supersecret123",
        "role": "ATTENDEE",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "attendee@example.com"
    assert "access_token" in body

    resp = client.post("/auth/login", json={"email": "attendee@example.com", "password": "supersecret123"})
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "ATTENDEE"


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={
        "email": "u2@example.com", "full_name": "U Two", "password": "correcthorsebattery", "role": "ATTENDEE",
    })
    resp = client.post("/auth/login", json={"email": "u2@example.com", "password": "wrongpassword"})
    assert resp.status_code == 401


def test_duplicate_registration_rejected(client):
    payload = {"email": "dup@example.com", "full_name": "Dup", "password": "password123", "role": "ATTENDEE"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_admin_only_user_listing(client):
    client.post("/auth/register", json={"email": "org@example.com", "full_name": "Org", "password": "password123", "role": "ORGANIZER"})
    login = client.post("/auth/login", json={"email": "org@example.com", "password": "password123"})
    token = login.json()["access_token"]

    resp = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403  # organizer cannot list all users

    admin_reg = client.post("/auth/register", json={"email": "admin@example.com", "full_name": "Admin", "password": "password123", "role": "ADMIN"})
    admin_token = admin_reg.json()["access_token"]
    resp = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

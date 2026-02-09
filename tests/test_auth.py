def test_register_user(client):
    payload = {
        "full_name": "Test User",
        "role": "client",
        "email": "test@example.com",
        "password": "12345678",
        "password_confirm": "12345678",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()


def test_login_user(client):
    payload = {
        "email": "test@example.com",
        "password": "12345678"
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    assert "access_token" in response.json()

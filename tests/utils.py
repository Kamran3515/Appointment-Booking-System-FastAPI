def register_and_login(client, role="client"):
    register_response = client.post("/auth/register", json={
        "full_name": "Test User",
        "email": f"{role}@test.com",
        "password": "123456",
        "password_confirm": "123456",
        "role": role
    })

    assert register_response.status_code in (200, 201)

    login_response = client.post(
        "/auth/login",
        json={
            "email": f"{role}@test.com",
            "password": "123456"
        }
    )
    print(login_response)
    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data

    return data["access_token"]

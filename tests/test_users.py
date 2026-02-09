from tests.utils import register_and_login
from tests.conftest import auth_headers
from app.models.user import User

def test_get_own_profile(client):
    token = register_and_login(client)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "client@test.com"


def test_create_availability_as_client_forbidden(client):
    payload = {
        "start_time": "2026-02-10T10:00:00",
        "end_time": "2026-02-10T11:00:00"
    }

    response = client.post(
        "/availability/create-availability",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 403

def test_create_appointment_fail_without_provider(client):
    payload = {
        "provider_id": "00000000-0000-0000-0000-000000000000",
        "service_id": "00000000-0000-0000-0000-000000000000",
        "start_time": "2026-02-10T10:00:00",
        "end_time": "2026-02-10T11:00:00"
    }

    response = client.post(
        "/appointments/",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code in (400, 404)

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_send_saved_course_email_accepts_request() -> None:
    response = client.post(
        "/api/v1/saved-courses/email",
        json={
            "recipient_email": "user@example.com",
            "course_title": "강남 감성 다이닝 데이트",
        },
    )

    assert response.status_code == 202

    payload = response.json()
    assert payload["status"] == "requested"
    assert payload["recipient_email"] == "user@example.com"
    assert payload["course_title"] == "강남 감성 다이닝 데이트"

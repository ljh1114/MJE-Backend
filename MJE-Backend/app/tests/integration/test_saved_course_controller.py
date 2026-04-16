from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_send_saved_course_email_accepts_request() -> None:
    response = client.post(
        "/api/v1/saved-courses/email",
        json={
            "recipient_email": "user@example.com",
            "course_id": "course-gangnam-main",
            "course_title": "강남 감성 다이닝 데이트",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "sent"
    assert payload["recipient_email"] == "user@example.com"
    assert payload["course_id"] == "course-gangnam-main"
    assert payload["course_title"] == "강남 감성 다이닝 데이트"


def test_send_saved_course_email_rejects_invalid_email() -> None:
    response = client.post(
        "/api/v1/saved-courses/email",
        json={
            "recipient_email": "not-an-email",
            "course_id": "course-gangnam-main",
            "course_title": "강남 감성 다이닝 데이트",
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "SAVED_COURSE_INVALID_REQUEST"
    assert response.json()["field"] == "recipient_email"


def test_send_saved_course_email_rejects_invalid_course_id() -> None:
    response = client.post(
        "/api/v1/saved-courses/email",
        json={
            "recipient_email": "user@example.com",
            "course_id": "gangnam-main",
            "course_title": "강남 감성 다이닝 데이트",
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "SAVED_COURSE_INVALID_REQUEST"
    assert response.json()["field"] == "course_id"

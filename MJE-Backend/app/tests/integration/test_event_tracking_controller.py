from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_collect_event_endpoint_accepts_event() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
            "session_id": "session-123",
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["event_id"]


def test_collect_event_endpoint_rejects_invalid_payload() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "EVENT_TRACKING_INVALID_REQUEST"
    assert payload["field"] == "session_id"

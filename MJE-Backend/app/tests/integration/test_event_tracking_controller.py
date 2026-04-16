from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _error_payload(response):
    body = response.json()
    detail = body.get("detail")
    if isinstance(detail, dict):
        return detail
    return body


def test_collect_event_endpoint_accepts_event() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
            "session_id": "sess_01HZ",
            "page_url": "https://example.com/planner",
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["event_id"]


def test_collect_event_endpoint_accepts_explore_click_event() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "date_course_explore_clicked",
            "session_id": "sess_01HZ",
            "page_url": "https://example.com/explore",
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
            "page_url": "https://example.com/planner",
        },
    )

    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_REQUEST"
    assert payload["field"] == "session_id"


def test_collect_event_endpoint_rejects_missing_page_url() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
            "session_id": "sess_01HZ",
        },
    )

    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_REQUEST"
    assert payload["field"] == "page_url"


def test_collect_event_endpoint_rejects_unknown_event_type() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "unknown_event",
            "session_id": "sess_01HZ",
            "page_url": "https://example.com/planner",
        },
    )

    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_REQUEST"
    assert payload["field"] == "event_type"


def test_collect_event_endpoint_rejects_invalid_session_id_domain_rules() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
            "session_id": "bad",
            "page_url": "https://example.com/planner",
        },
    )

    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_INPUT"
    assert payload["field"] == "session_id"

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
            "attempt_id": "att_01HZXY",
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
            "attempt_id": "att_01HZXY",
        },
    )

    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_INPUT"
    assert payload["field"] == "session_id"


def test_collect_event_endpoint_persists_row_with_sqlite_repository_override() -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    from app.core.database import Base
    from app.domains.event_tracking.event_tracking_dependencies import (
        get_event_tracking_repository,
    )
    from app.domains.event_tracking.repositories.event_tracking_repository import (
        SqlAlchemyEventTrackingRepository,
    )
    from app.domains.event_tracking.repositories.tracking_event_row import (
        TrackingEventRow,
    )
    from app.main import app

    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    repository = SqlAlchemyEventTrackingRepository(engine)

    app.dependency_overrides[get_event_tracking_repository] = lambda: repository
    try:
        response = client.post(
            "/api/v1/events",
            json={
                "event_type": "create_course_clicked",
                "session_id": "sess_01HZ",
                "page_url": "https://example.com/planner",
                "attempt_id": "att_01HZXY",
            },
        )
        assert response.status_code == 202
        event_id = response.json()["event_id"]
        with Session(engine) as session:
            row = session.scalars(
                select(TrackingEventRow).where(TrackingEventRow.id == event_id)
            ).one()
        assert row.event_type == "create_course_clicked"
        assert row.session_id == "sess_01HZ"
        assert row.event_payload["page_url"] == "https://example.com/planner"
        assert row.attempt_id == "att_01HZXY"
        assert row.event_payload["attempt_id"] == "att_01HZXY"
    finally:
        app.dependency_overrides.clear()


def test_collect_event_endpoint_returns_503_when_persistence_fails() -> None:
    from app.domains.event_tracking.entities.tracking_event import TrackingEvent
    from app.domains.event_tracking.event_tracking_dependencies import (
        get_event_tracking_repository,
    )
    from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
        EventTrackingPersistenceError,
    )
    from app.domains.event_tracking.repositories.event_tracking_repository import (
        EventTrackingRepository,
    )
    from app.main import app

    class FailingRepository(EventTrackingRepository):
        def save(self, event: TrackingEvent) -> None:
            raise EventTrackingPersistenceError(
                session_id=event.session_id,
                event_type=event.event_type,
            )

        def find_by_session_id(self, session_id: str) -> list[TrackingEvent]:
            return []

    app.dependency_overrides[get_event_tracking_repository] = (
        lambda: FailingRepository()
    )
    try:
        response = client.post(
            "/api/v1/events",
            json={
                "event_type": "create_course_clicked",
                "session_id": "sess_01HZ",
                "page_url": "https://example.com/planner",
                "attempt_id": "att_01HZXY",
            },
        )
        assert response.status_code == 503
        payload = _error_payload(response)
        assert payload["code"] == "EVENT_TRACKING_PERSISTENCE_FAILED"
        assert payload["session_id"] == "sess_01HZ"
        assert payload["event_type"] == "create_course_clicked"
    finally:
        app.dependency_overrides.clear()


def test_collect_event_endpoint_rejects_invalid_json_body() -> None:
    response = client.post(
        "/api/v1/events",
        content="{not-json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "EVENT_TRACKING_INVALID_REQUEST"
    assert payload["field"] == "body"
    assert "JSON" in payload["message"]


def test_collect_event_endpoint_rejects_wrong_type_for_page_url() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
            "session_id": "sess_01HZ",
            "page_url": 12345,
            "attempt_id": "att_01HZXY",
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "EVENT_TRACKING_INVALID_REQUEST"
    assert payload["field"] == "page_url"


def test_collect_event_endpoint_returns_500_on_unexpected_service_failure() -> None:
    from unittest.mock import MagicMock

    from app.domains.event_tracking.event_tracking_dependencies import (
        get_event_tracking_service,
    )
    from app.main import app

    mock_service = MagicMock()
    mock_service.collect_event.side_effect = RuntimeError("simulated failure")

    app.dependency_overrides[get_event_tracking_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/events",
            json={
                "event_type": "create_course_clicked",
                "session_id": "sess_01HZ",
                "page_url": "https://example.com/planner",
                "attempt_id": "att_01HZXY",
            },
        )
        assert response.status_code == 500
        payload = _error_payload(response)
        assert payload["code"] == "EVENT_TRACKING_INTERNAL_ERROR"
    finally:
        app.dependency_overrides.clear()


def test_collect_event_endpoint_requires_attempt_id_for_exploration_start() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "create_course_clicked",
            "session_id": "sess_01HZ",
            "page_url": "https://example.com/planner",
        },
    )
    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_INPUT"
    assert payload["field"] == "attempt_id"


def test_collect_event_endpoint_accepts_save_course_clicked() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "save_course_clicked",
            "session_id": "sess_01HZ",
            "page_url": "https://example.com/planner",
            "attempt_id": "att_01HZXY",
        },
    )
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"


def test_collect_event_endpoint_rejects_attempt_id_for_explore_click() -> None:
    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "date_course_explore_clicked",
            "session_id": "sess_01HZ",
            "page_url": "https://example.com/explore",
            "attempt_id": "att_01HZXY",
        },
    )
    assert response.status_code == 400
    payload = _error_payload(response)
    assert payload["code"] == "EVENT_TRACKING_INVALID_INPUT"
    assert payload["field"] == "attempt_id"


def test_collect_event_endpoint_returns_409_on_duplicate_save_click() -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool

    from app.core.database import Base
    from app.domains.event_tracking.event_tracking_dependencies import (
        get_event_tracking_repository,
    )
    from app.domains.event_tracking.repositories.event_tracking_repository import (
        SqlAlchemyEventTrackingRepository,
    )
    from app.main import app

    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    repository = SqlAlchemyEventTrackingRepository(engine)

    body = {
        "event_type": "save_course_clicked",
        "session_id": "sess_01HZ",
        "page_url": "https://example.com/planner",
        "attempt_id": "att_01HZXY",
    }

    app.dependency_overrides[get_event_tracking_repository] = lambda: repository
    try:
        assert client.post("/api/v1/events", json=body).status_code == 202
        dup = client.post("/api/v1/events", json=body)
        assert dup.status_code == 409
        detail = _error_payload(dup)
        assert detail["code"] == "EVENT_TRACKING_DUPLICATE_EVENT"
        assert detail["session_id"] == "sess_01HZ"
        assert detail["attempt_id"] == "att_01HZXY"
        assert detail["field"] == "attempt_id"
    finally:
        app.dependency_overrides.clear()

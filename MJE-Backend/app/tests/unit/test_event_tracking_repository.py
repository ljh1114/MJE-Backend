from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.domains.event_tracking.entities.tracking_event import TrackingEvent
from app.domains.event_tracking.exceptions.event_tracking_exceptions import (
    EventTrackingDuplicateEventError,
    EventTrackingPersistenceError,
)
from app.domains.event_tracking.repositories.event_tracking_repository import (
    SqlAlchemyEventTrackingRepository,
)
from app.domains.event_tracking.repositories.tracking_event_row import TrackingEventRow


def test_sqlalchemy_repository_inserts_tracking_event_row() -> None:
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    repo = SqlAlchemyEventTrackingRepository(engine)
    event_id = uuid4()
    event = TrackingEvent(
        id=event_id,
        session_id="sess_01HZ",
        user_id=None,
        event_type="date_course_explore_clicked",
        event_payload={"page_url": "https://example.com/explore"},
        occurred_at=datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc),
    )

    repo.save(event)

    with Session(engine) as session:
        row = session.scalars(select(TrackingEventRow)).one()
    assert row.id == str(event_id)
    assert row.event_type == "date_course_explore_clicked"
    assert row.event_payload["page_url"] == "https://example.com/explore"


def test_sqlalchemy_repository_maps_db_errors_to_domain_error() -> None:
    engine = create_engine("sqlite:///:memory:")
    repo = SqlAlchemyEventTrackingRepository(engine)
    event = TrackingEvent(
        id=uuid4(),
        session_id="sess_01HZ",
        user_id=None,
        event_type="create_course_clicked",
        event_payload={"page_url": "https://example.com/p"},
        occurred_at=datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc),
    )

    try:
        repo.save(event)
    except EventTrackingPersistenceError:
        return
    raise AssertionError("Expected EventTrackingPersistenceError")


def test_sqlalchemy_repository_find_by_session_id_ordered() -> None:
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    repo = SqlAlchemyEventTrackingRepository(engine)
    sid = "sess_01HZ"
    t_early = datetime(2026, 4, 17, 10, 0, tzinfo=timezone.utc)
    t_late = datetime(2026, 4, 17, 11, 0, tzinfo=timezone.utc)
    e1 = TrackingEvent(
        id=uuid4(),
        session_id=sid,
        user_id=None,
        event_type="create_course_clicked",
        event_payload={"page_url": "https://example.com/p"},
        occurred_at=t_late,
    )
    e0 = TrackingEvent(
        id=uuid4(),
        session_id=sid,
        user_id=None,
        event_type="date_course_explore_clicked",
        event_payload={"page_url": "https://example.com/e"},
        occurred_at=t_early,
    )
    repo.save(e1)
    repo.save(e0)

    found = repo.find_by_session_id(sid)
    assert [e.event_type for e in found] == [
        "date_course_explore_clicked",
        "create_course_clicked",
    ]
    assert found[0].occurred_at < found[1].occurred_at


def test_sqlalchemy_repository_rejects_duplicate_save_click_same_attempt() -> None:
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    repo = SqlAlchemyEventTrackingRepository(engine)
    sid = "sess_01HZ"
    aid = "att_dup"
    t0 = datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc)
    payload = {
        "page_url": "https://example.com/p",
        "attempt_id": aid,
    }
    first = TrackingEvent(
        id=uuid4(),
        session_id=sid,
        user_id=None,
        event_type="save_course_clicked",
        event_payload=payload,
        occurred_at=t0,
        attempt_id=aid,
    )
    duplicate = TrackingEvent(
        id=uuid4(),
        session_id=sid,
        user_id=None,
        event_type="save_course_clicked",
        event_payload=payload,
        occurred_at=t0,
        attempt_id=aid,
    )
    repo.save(first)
    try:
        repo.save(duplicate)
    except EventTrackingDuplicateEventError:
        return
    raise AssertionError("Expected EventTrackingDuplicateEventError for duplicate save")

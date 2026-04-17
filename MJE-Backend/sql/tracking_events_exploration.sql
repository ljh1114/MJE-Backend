-- 탐색 성과(MJE-BE-9)용 tracking_events 확장 (PostgreSQL 수동 마이그레이션 예시)
-- 기존 테이블이 이미 있는 환경에서만 실행한다. 신규 배포는 ORM create_all/migrate 정책에 따른다.

ALTER TABLE tracking_events
    ADD COLUMN IF NOT EXISTS attempt_id VARCHAR(128);

CREATE INDEX IF NOT EXISTS ix_tracking_events_session_id_attempt_id
    ON tracking_events (session_id, attempt_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_tracking_events_save_click_once_per_attempt
    ON tracking_events (session_id, attempt_id)
    WHERE event_type = 'save_course_clicked' AND attempt_id IS NOT NULL;

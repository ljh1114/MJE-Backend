-- tracking_events: 사용자 행동 이벤트 공통 적재 테이블 (PRD 10.3 TrackingEvent)
-- 대상: 데이트 코스 탐색 클릭(date_course_explore_clicked), 코스 생성 클릭(create_course_clicked) 등
--
-- id는 애플리케이션에서 생성(UUID 문자열)하여 API event_id와 일치시킵니다.

CREATE TABLE IF NOT EXISTS tracking_events (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL,
    user_id VARCHAR(64) NULL,
    event_type VARCHAR(64) NOT NULL,
    event_payload JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE tracking_events IS '클라이언트 전송 이벤트(유형 + JSON 페이로드) 적재';

COMMENT ON COLUMN tracking_events.id IS '이벤트 고유 ID (API 응답 event_id와 동일)';

COMMENT ON COLUMN tracking_events.session_id IS '인증 전까지 익명 세션 식별자';

COMMENT ON COLUMN tracking_events.user_id IS '로그인 사용자 식별자(도입 시 사용)';

COMMENT ON COLUMN tracking_events.event_type IS '이벤트 유형(예: date_course_explore_clicked)';

COMMENT ON COLUMN tracking_events.event_payload IS '이벤트별 속성(JSON). 민감정보 저장 금지';

COMMENT ON COLUMN tracking_events.occurred_at IS '서버 수신(또는 정규화) 시각';

CREATE INDEX IF NOT EXISTS ix_tracking_events_event_type_occurred_at ON tracking_events (event_type, occurred_at DESC);

CREATE INDEX IF NOT EXISTS ix_tracking_events_session_occurred_at ON tracking_events (session_id, occurred_at DESC);

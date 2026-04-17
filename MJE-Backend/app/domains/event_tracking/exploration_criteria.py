"""데이트 코스 탐색 성과 판단 기준 (MJE-BE-9).

SC 요약
- 탐색 시작: 코스 **생성하기** 버튼 클릭에 대응하는 이벤트.
- 탐색 성공(탐색 완료): 동일 탐색 시도에서 생성 클릭 이후 **저장하기 버튼 클릭**이 있는 경우.
  성공 여부는 **버튼 클릭**만으로 판단하며, 실제 코스 DB 저장 성공 여부는 포함하지 않는다.
- 탐색 실패(탐색 미완료): 동일 시도에서 저장하기 버튼 클릭이 없는 경우.
  **실패 전용 이벤트는 기록하지 않으며**, 저장 클릭 이벤트 부재로만 판단한다.
- 동일 탐색 시도에서 저장 관련 처리는 1회만 유효(별도 중복 처리 로직에서 보장).

`event_type` 문자열과 `event_payload` 키는 API·저장 스키마와 동일해야 한다.
"""

from __future__ import annotations

from enum import StrEnum


class ExplorationOutcome(StrEnum):
    """집계·판단 결과. 실패는 DB에 별도 행으로 넣지 않고 이 값으로만 표현한다."""

    SUCCESS = "success"
    """생성 이벤트와 저장 버튼 클릭 이벤트가 같은 탐색 시도에 존재."""

    NOT_COMPLETED = "not_completed"
    """생성은 있으나 같은 탐색 시도에 저장 버튼 클릭 이벤트가 없음 (탐색 미완료)."""


# --- 이벤트 타입 (tracking_events.event_type) --------------------------------

EXPLORATION_START_EVENT_TYPE = "create_course_clicked"
"""탐색 행동 시작: 코스 생성하기 버튼 클릭."""

EXPLORATION_SAVE_CLICK_EVENT_TYPE = "save_course_clicked"
"""탐색 성공 판정에 사용하는 저장하기 버튼 클릭 (수집 API에서 별도로 정의·수신)."""

# 기존 탐색/플래너 진입 등 다른 추적 이벤트 (탐색 성과 '시작'과는 구분)
DATE_COURSE_EXPLORE_CLICKED_EVENT_TYPE = "date_course_explore_clicked"


# --- 페이로드 (event_payload JSON) -------------------------------------------

ATTEMPT_ID_PAYLOAD_KEY = "attempt_id"
"""동일 탐색 시도를 묶기 위한 클라이언트 생성 ID. 중복 1회 처리·짝 맞추기에 사용."""


def is_exploration_flow_event_type(event_type: str) -> bool:
    """탐색 성과 판단에 쓰이는 시작·저장 클릭 타입인지 여부."""
    return event_type in (
        EXPLORATION_START_EVENT_TYPE,
        EXPLORATION_SAVE_CLICK_EVENT_TYPE,
    )

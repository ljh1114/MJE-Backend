# MJE Backend PRD

## 1. 문서 목적

이 문서는 데이트 코스 추천 웹 서비스의 백엔드 제품 요구사항과 기술 설계 기준을 정의한다.  
서비스 대상은 데이트 장소, 활동, 이동 동선을 한 번에 정하기 어려운 20~30대 사용자이며, 백엔드는 추천 생성, 코스 저장, 사용자 행동 추적을 안정적으로 처리해야 한다.

본 문서는 `README.md`의 Layered Architecture 원칙을 기반으로 작성하며, 유지보수성과 확장성을 최우선으로 한다.

## 2. 서비스 개요

### 2.1 서비스 한 줄 설명

사용자의 상황과 취향을 기반으로 데이트 장소와 활동을 조합해 데이트 코스를 추천하고, 마음에 드는 코스를 저장하며, 사용자 행동 데이터를 수집해 추천 품질을 개선하는 웹 서비스

### 2.2 핵심 사용자 문제

- 어디서 데이트할지 결정하기 어렵다.
- 무엇을 할지 한 번에 정하기 어렵다.
- 이동 동선까지 포함한 자연스러운 코스를 직접 짜기 번거롭다.
- 이전에 마음에 들었던 코스를 다시 찾기 어렵다.

### 2.3 백엔드 목표

- 입력 조건에 맞는 데이트 코스를 일관된 형태로 추천한다.
- 추천 결과를 사용자가 저장하고 다시 조회할 수 있게 한다.
- 사용자 행동 이벤트를 수집하여 향후 추천 개선 근거로 활용한다.
- 도메인 단위로 분리된 구조를 통해 기능 확장과 운영을 쉽게 한다.

## 3. 도메인 정의

백엔드는 아래 3개 도메인으로 구성한다.

### 3.1 `recommendation`

역할:

- 사용자 입력 조건(지역, 분위기, 예산, 선호 활동 등)을 기반으로 데이트 코스를 생성한다.
- 장소 후보와 활동 후보를 조합하여 코스 단위를 만든다.
- 추천 결과를 응답 DTO로 반환한다.

핵심 책임:

- 추천 요청 검증
- 추천 유스케이스 실행
- 추천 결과 조합
- 추천 기준 및 정책 관리

예상 주요 기능:

- 추천 요청 생성
- 추천 결과 조회
- 추천 결과 상세 조회
- 향후 개인화 추천 확장

### 3.2 `saved_course`

역할:

- 사용자가 추천받은 코스를 저장, 조회, 삭제할 수 있도록 한다.
- 사용자의 재방문과 비교 검토를 지원한다.

핵심 책임:

- 저장 가능한 코스 구조 관리
- 사용자별 저장 목록 조회
- 저장 코스 상세 조회
- 삭제 및 중복 저장 방지

예상 주요 기능:

- 코스 저장
- 저장 목록 조회
- 저장 상세 조회
- 저장 취소

### 3.3 `event_tracking`

역할:

- 추천 요청, 추천 클릭, 저장, 상세 조회 등 사용자 행동 이벤트를 기록한다.
- 서비스 개선 및 추천 품질 고도화에 필요한 분석 기반을 만든다.

핵심 책임:

- 이벤트 수집 API 제공
- 이벤트 표준 스키마 관리
- 이벤트 저장
- 향후 분석 시스템 연계 기반 제공

예상 주요 기능:

- 이벤트 적재
- 이벤트 유형 관리
- 추천 성과 분석용 데이터 축적

## 4. 주요 사용자 흐름

### 4.1 추천 생성 흐름

1. 사용자가 조건을 입력한다.
2. `recommendation` Controller가 요청 DTO를 검증한다.
3. Service가 추천 생성 유스케이스를 실행한다.
4. Repository가 필요한 장소/코스 데이터에 접근한다.
5. Service가 코스를 조합하고 비즈니스 규칙을 적용한다.
6. Controller가 Response DTO로 변환해 응답한다.

### 4.2 저장 흐름

1. 사용자가 추천 결과 중 원하는 코스를 저장한다.
2. `saved_course` Controller가 요청을 수신한다.
3. Service가 사용자 정보와 코스 저장 가능 여부를 검증한다.
4. Repository가 저장 데이터를 기록한다.
5. 저장 결과를 Response DTO로 반환한다.

### 4.3 이벤트 추적 흐름

1. 사용자의 추천 요청, 클릭, 저장, 상세 조회 등의 행동이 발생한다.
2. `event_tracking` Controller가 이벤트 DTO를 수신한다.
3. Service가 이벤트 유효성을 확인한다.
4. Repository가 이벤트를 저장한다.
5. 추후 추천 개선 및 운영 지표 분석에 활용한다.

## 5. 백엔드 기술 스택

추천하는 초기 기술 스택은 다음과 같다.

### 5.1 Language / Framework

- Python 3.12
- FastAPI

선정 이유:

- 타입 힌트 기반 개발이 가능하다.
- DTO, 검증, 문서화에 강점이 있다.
- 비동기 처리 및 확장에 유리하다.

### 5.2 Validation / Schema

- Pydantic v2

선정 이유:

- Request/Response DTO를 명확히 분리할 수 있다.
- Layered Architecture에서 Entity와 DTO를 엄격히 나누기 좋다.

### 5.3 Database

- PostgreSQL

선정 이유:

- 안정적인 관계형 데이터 관리에 적합하다.
- 추천 결과 저장, 사용자 저장 코스, 이벤트 적재를 구조적으로 관리하기 좋다.

### 5.4 ORM / Persistence

- SQLAlchemy 2.x
- Alembic

선정 이유:

- Repository 계층 구현에 적합하다.
- 마이그레이션 관리가 가능하다.

### 5.5 Cache / Async Extension

- Redis

선정 이유:

- 자주 요청되는 추천 결과 캐싱에 활용 가능하다.
- 향후 비동기 처리, 큐, rate limiting 확장에 유리하다.

### 5.6 Testing

- pytest
- httpx

선정 이유:

- Service 단위 테스트와 API 통합 테스트 구성이 쉽다.

### 5.7 Quality / Tooling

- ruff
- black
- mypy

선정 이유:

- 코드 스타일, 정적 검사, 유지보수성 확보에 유리하다.

### 5.8 Deployment / Runtime

- Docker
- Docker Compose
- Uvicorn

## 6. 아키텍처 원칙

`README.md` 기준 Layered Architecture를 반드시 따른다.

기본 호출 흐름:

`Controller -> Service -> Repository`

핵심 원칙:

- Controller는 요청/응답과 DTO 검증만 담당한다.
- Service는 유스케이스와 비즈니스 로직을 담당한다.
- Repository는 DB 접근만 담당한다.
- Entity는 도메인 데이터와 상태만 표현한다.
- Entity를 API 응답으로 직접 반환하지 않는다.
- 트랜잭션 경계는 Service에 둔다.
- Repository의 내부 예외는 필요 시 Service에서 비즈니스 예외로 변환한다.

금지 사항:

- Controller에 비즈니스 로직 작성 금지
- Service에서 DB 직접 접근 금지
- Repository에 비즈니스 정책 작성 금지
- Entity에서 외부 API/DB/다른 계층 의존성 사용 금지

## 7. 백엔드 폴더 구조 제안

```text
MJE-Backend/
  app/
    main.py
    core/
      config.py
      database.py
      exceptions.py
      logging.py
    domains/
      recommendation/
        controllers/
          recommendation_controller.py
        services/
          recommendation_service.py
        repositories/
          recommendation_repository.py
        entities/
          recommendation.py
          course.py
        dtos/
          recommendation_request.py
          recommendation_response.py
        exceptions/
          recommendation_exceptions.py
      saved_course/
        controllers/
          saved_course_controller.py
        services/
          saved_course_service.py
        repositories/
          saved_course_repository.py
        entities/
          saved_course.py
        dtos/
          save_course_request.py
          saved_course_response.py
        exceptions/
          saved_course_exceptions.py
      event_tracking/
        controllers/
          event_tracking_controller.py
        services/
          event_tracking_service.py
        repositories/
          event_tracking_repository.py
        entities/
          tracking_event.py
        dtos/
          event_request.py
          event_response.py
        exceptions/
          event_tracking_exceptions.py
    shared/
      dto/
      enums/
      utils/
    tests/
      unit/
      integration/
  alembic/
  requirements/
    base.txt
    dev.txt
  Dockerfile
  docker-compose.yml
  pyproject.toml
  README.md
```

## 8. 도메인별 계층 책임

### 8.1 Controller

역할:

- HTTP 요청 수신
- Request DTO 검증
- Service 호출
- Response DTO 반환
- 예외를 HTTP 응답으로 매핑

예시:

- `recommendation_controller.py`: 추천 생성/조회 API
- `saved_course_controller.py`: 저장/조회/삭제 API
- `event_tracking_controller.py`: 이벤트 수집 API

### 8.2 Service

역할:

- 유스케이스 실행
- 도메인 정책 적용
- 여러 Repository 조합
- 트랜잭션 경계 관리

예시:

- `RecommendationService`: 조건 기반 코스 생성
- `SavedCourseService`: 저장 중복 방지 및 사용자별 조회
- `EventTrackingService`: 이벤트 정규화 및 적재

### 8.3 Repository

역할:

- DB CRUD 처리
- 조회 조건별 데이터 접근 캡슐화
- ORM/SQL 세부 구현 담당

### 8.4 Entity

역할:

- 도메인 데이터와 상태 표현
- 자기 자신과 직접 관련된 최소 규칙만 포함

예시:

- `Course`
- `Recommendation`
- `SavedCourse`
- `TrackingEvent`

### 8.5 DTO

역할:

- API 입력과 출력 모델 분리
- 외부 계약 안정성 보장
- 내부 Entity와 API 스펙 분리

## 9. 초기 API 범위

### 9.1 `recommendation`

- `POST /api/v1/recommendations`
- `GET /api/v1/recommendations/{recommendation_id}`

요청 예시 필드:

- 지역
- 예산 범위
- 선호 분위기
- 선호 활동
- 데이트 시간대

응답 예시 필드:

- 추천 ID
- 코스 제목
- 코스 설명
- 장소 목록
- 예상 예산
- 예상 소요 시간

### 9.2 `saved_course`

- `POST /api/v1/saved-courses`
- `GET /api/v1/saved-courses`
- `GET /api/v1/saved-courses/{saved_course_id}`
- `DELETE /api/v1/saved-courses/{saved_course_id}`

### 9.3 `event_tracking`

- `POST /api/v1/events`

이벤트 예시:

- recommendation_requested
- recommendation_viewed
- course_saved
- saved_course_opened

## 10. 데이터 설계 초안

### 10.1 Recommendation

주요 속성 예시:

- id
- user_id 또는 session_id
- input_context
- generated_courses
- created_at

### 10.2 SavedCourse

주요 속성 예시:

- id
- user_id
- recommendation_id
- course_snapshot
- created_at

### 10.3 TrackingEvent

주요 속성 예시:

- id
- user_id 또는 session_id
- event_type
- event_payload
- occurred_at

## 11. 비기능 요구사항

### 11.1 유지보수성

- 도메인 단위 디렉터리 분리
- 계층별 책임 분리
- DTO, Entity, Repository 역할 엄격 분리
- 공통 설정은 `core`와 `shared`에 한정

### 11.2 확장성

- 도메인 추가 시 `domains/<new_domain>` 구조만 확장하면 되도록 설계
- 추천 로직 고도화 시 Service 내부 정책 객체 또는 별도 전략 모듈로 분리 가능하게 설계
- 이벤트 적재는 추후 메시지 큐 또는 데이터 웨어하우스 연동 가능하게 설계

### 11.3 관측 가능성

- 요청 단위 로깅
- 예외 로깅 표준화
- 추천 요청 수, 저장 수, 이벤트 수를 기본 운영 지표로 관리

### 11.4 테스트 가능성

- Service는 단위 테스트 중심
- Controller는 API 통합 테스트 중심
- Repository는 DB 연동 테스트 최소 범위로 관리

## 12. 예외 처리 정책

- Controller는 내부 예외를 직접 노출하지 않는다.
- Service는 Repository 예외를 비즈니스 예외로 변환할 수 있다.
- 응답은 표준 에러 포맷을 사용한다.

권장 에러 응답 예시:

- `code`
- `message`
- `detail`
- `trace_id`

## 13. 보안 및 운영 고려사항

- 사용자 식별값은 인증 체계 도입 전까지 세션 또는 임시 식별자로 처리 가능
- 입력값 검증은 DTO 계층에서 우선 처리
- 이벤트 payload에는 민감정보 저장 금지
- 환경 변수 기반 설정 관리
- 운영/개발 환경 분리

## 14. 향후 확장 방향

- 사용자 인증 및 마이페이지 연동
- 개인화 추천
- 외부 장소 데이터 연동
- 인기 데이트 코스 랭킹
- 이벤트 분석 대시보드
- 비동기 추천 생성 또는 배치 재추천

## 15. 구현 우선순위

### Phase 1

- FastAPI 프로젝트 초기 세팅
- PostgreSQL, SQLAlchemy, Alembic 연동
- Layered Architecture 기본 골격 생성
- `recommendation`, `saved_course`, `event_tracking` 도메인 생성

### Phase 2

- 추천 생성 API 구현
- 저장 API 구현
- 이벤트 수집 API 구현

### Phase 3

- 테스트 코드 정비
- 캐시 적용
- 운영 로그/모니터링 정비

## 16. 최종 기준

이 백엔드의 첫 번째 목표는 "빠르게 만드는 것"이 아니라 "계속 확장 가능한 구조로 만드는 것"이다.  
따라서 모든 구현은 아래 기준을 만족해야 한다.

- 도메인 경계가 명확할 것
- 계층 책임이 섞이지 않을 것
- DTO와 Entity가 분리될 것
- Service가 유스케이스 중심으로 설계될 것
- 이후 추천 고도화와 이벤트 분석 확장을 수용할 수 있을 것

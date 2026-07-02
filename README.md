# MJE Backend — Dehangsa

### 1-1. 프로젝트 소개

Dehangsa는 20~30대를 위한 맞춤형 데이트 코스 추천 서비스입니다.

- 사용자가 지역, 시간, 이동수단 정보를 입력하면 조건에 맞는 데이트 코스를 자동으로 추천합니다.
- 추천 코스는 Main Course 1개와 Sub Course 2개로 구성되며, 사용자는 원하는 코스를 확인하고 링크로 공유할 수 있습니다.

### 1-2. 문제 정의

사용자 인터뷰와 관찰을 통해 20~30대 사용자가 데이트 코스를 계획하는 과정에서 반복적인 탐색 피로를 겪는다는 점을 확인했습니다.

- 데이트 코스를 정할 때 사용자는 지역, 시간, 이동수단, 상대방의 취향, 분위기, 예산 등 다양한 요소를 함께 고려해야 합니다.
- 여러 장소를 탐색하고 비교하지만, 적절한 코스를 찾지 못하면 다시 검색을 반복하게 됩니다.
- 결과적으로 탐색 실패가 재탐색 루프로 이어지고, 의사결정 피로도가 증가하면서 계획 수립을 포기하거나 서비스에서 이탈하는 문제가 발생했습니다.

→ 따라서 Dehangsa는 사용자의 조건에 맞는 데이트 코스를 빠르게 추천함으로써 탐색 부담을 줄이고, 데이트 계획 수립 과정을 더 쉽게 만드는 것을 목표로 했습니다.

### 1-3. 해결 방안

**사용자 맞춤 데이트 코스 추천**
- 사용자의 상황과 조건을 기반으로 데이트 코스를 추천하여, 직접 장소를 탐색하고 조합해야 하는 부담을 줄이고자 했습니다.

**기대 효과**
- **탐색 범위 감소**: 여러 플랫폼에서 장소를 직접 비교하지 않아도 되도록 추천 코스를 제공
- **의사결정 피로도 완화**: 선택지를 무작위로 많이 제공하기보다, 상황에 맞는 코스를 제안해 결정 부담 감소
- **핵심 행동 측정 용이**: 추천 결과 카드 클릭률, 코스 생성률, 공유 클릭률 등을 통해 사용자 반응 확인 가능

---

### 2-1. 핵심 기능

초기 MVP 단계에서 탐색 진입을 원활하게 하는 것을 목적으로, 프론트엔드 클라이언트에 사용자 맞춤 데이트 코스 추천 기능을 제공하는 FastAPI 기반 백엔드 서버입니다.

- **코스 추천 생성**: 지역·시간·이동수단 조건을 입력받아 Redis 캐시된 장소 후보 중 Main Course 1개 + Sub Course 2개를 조합해 추천 (`POST /courses/recommendations`)
- **코스 상세 조회**: 코스에 포함된 장소(식당/카페/액티비티)의 좌표·주소·영업 정보를 제공, 다른 코스 목록 조회 API 별도 제공 (`GET /courses/{course_id}`, `GET /recommendations/detail/{course_id}/...`)
- **코스 공유 로그**: 공유/내보내기 행동을 기록하는 export_logs API 제공 (`POST /api/v1/export-logs` — course_export, course_send, export_close)
- **행동 이벤트 트래킹**: 랜딩/홈/코스 화면의 주요 클릭·조회 이벤트를 세션 단위로 수신·저장 (`POST /landing/events`, `POST /home/events`, `POST /courses/events`)
- **영속 저장**: 생성된 코스와 이벤트 로그를 MySQL에 비동기로 저장

### 2-2. 시스템 구성

```
Client
  └─▶ FastAPI (dehangsa.com)
         ├─▶ MySQL (aiomysql, 비동기)   ← 코스/이벤트 영속 저장
         ├─▶ Redis                       ← 후보 장소 캐시
         └─▶ Kakao Map REST API          ← 장소 검색 / 지오코딩
```

- **애플리케이션 서버**: FastAPI + Uvicorn
- **배포 환경**: AWS EC2 + Docker + CloudFront
- **데이터베이스**: MySQL (비동기 커넥션 풀)
- **캐시**: Redis
- **외부 API**: Kakao Map REST API

### 2-3. 기술 스택

| 분류 | 라이브러리 | 버전 |
|------|-----------|------|
| 웹 프레임워크 | FastAPI | ≥ 0.115.0 |
| ASGI 서버 | Uvicorn | ≥ 0.32.0 |
| ORM | SQLAlchemy (asyncio) | ≥ 2.0.0 |
| DB 드라이버 | aiomysql | 0.1.1 |
| 캐시 클라이언트 | redis[asyncio] | ≥ 5.0.0 |
| 스키마 / 검증 | Pydantic v2, pydantic-settings | ≥ 2.0.0 |
| DB 마이그레이션 | Alembic | ≥ 1.13.0 |
| HTTP 클라이언트 | httpx | ≥ 0.27.0 |
| 환경 변수 | python-dotenv | ≥ 1.0.0 |

### 2-4. 프로젝트 구조

FastAPI 기반 Layered Architecture + DDD 구조를 따릅니다.

```
MJE-Backend/
├── main.py                        # 앱 진입점, 라우터 등록, 미들웨어 설정
└── app/
    ├── common/                    # 공통 예외 / 핸들러
    ├── domains/
    │   ├── home/                  # 홈 화면 이벤트 도메인
    │   │   ├── domain/            # Entity, Value Object, Events, Domain Service
    │   │   ├── service/           # UseCase, DTO (request/response)
    │   │   ├── controller/api/    # Router, RequestForm, ResponseForm
    │   │   └── repository/        # ORM 모델, Mapper
    │   │
    │   ├── landing/               # 랜딩 페이지 이벤트 도메인
    │   │   └── (home과 동일 구조)
    │   │
    │   ├── recommendation/        # 데이트 코스 추천 도메인
    │   │   ├── domain/
    │   │   ├── service/           # GetRecommendationUseCase
    │   │   ├── controller/api/    # /courses/recommendations
    │   │   └── repository/
    │   │
    │   └── courses/               # 코스 관리 도메인
    │       ├── domain/
    │       ├── service/           # CreateCourse, GetCourseDetail UseCase
    │       ├── controller/api/    # /courses 라우터
    │       └── repository/        # CourseOrm, CoursePlaceOrm
    │
    └── infrastructure/
        ├── database/              # SQLAlchemy 엔진, 세션, Base
        ├── cache/                 # Redis 클라이언트, 후보 캐시
        ├── config/                # pydantic-settings 기반 환경 변수
        └── api/
            ├── search/            # KakaoSearchClient
            ├── geocoding/         # KakaoGeocodingClient
            ├── map/               # KakaoMapClient
            └── export_logs/       # 내보내기 로그 (ORM, Router)
```

**의존성 방향**: `Controller → Service → Domain ← Repository ← Infrastructure`

### 2-5. 데이터베이스

MySQL을 사용하며, SQLAlchemy 비동기 ORM으로 접근합니다.

| 테이블 | 설명 |
|--------|------|
| `courses` | 생성된 데이트 코스 (course_id, session_id, grade, area, transport 등) |
| `course_places` | 코스에 포함된 장소 목록 (courses.course_id FK, place_order, place_type 등) |
| `home_events` | 홈 화면 이벤트 로그 (view_home, logo_click, home_click) |
| `landing_events` | 랜딩 페이지 이벤트 로그 | (view_landing, landing_top. landing_bottom) |
| `courses_events` | 코스 화면 이벤트 로그 (course_create, card_click, tryagain_click 등) |
| `export_logs` | 코스 내보내기 로그 (course_export, course_send, export_close) |

### 2-6. API

본 프로젝트는 Swagger를 통해 API를 시각화하고 테스트할 수 있도록 제공합니다.
서버 실행 후 아래의 주소를 통해 전체 API 명세를 확인할 수 있습니다.

Local 환경 (로컬 테스트): `http://localhost:33333/docs`
Base URL: `https://d3580l6z7ujilw.cloudfront.net`

#### System

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/health` | 헬스 체크 |
| `DELETE` | `/admin/cache/candidates` | 후보 장소 Redis 캐시 전체 삭제 |

#### Home

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/home/events` | 홈 화면 이벤트 기록 (view_home, logo_click, home_click) |

#### Landing

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/landing/events` | 랜딩 페이지 이벤트 기록 |

#### Courses

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/courses/recommendations` | 데이트 코스 추천 생성 (Kakao 장소 검색 + Redis 캐시 활용) |
| `GET` | `/courses/{course_id}` | 코스 상세 조회 |
| `POST` | `/courses/events` | 코스 화면 이벤트 기록 (course_create, card_click 등) |

#### Recommendation (상세 조회)

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/courses/recommendations/{course_id}` | 코스 전체 상세 조회 |
| `GET` | `/recommendations/courses/{course_id}` | 코스 상세 (프론트엔드용) |
| `GET` | `/recommendations/detail/{course_id}/other-courses` | 같은 세션의 다른 코스 목록 |
| `GET` | `/recommendations/detail/{course_id}/activities` | 코스 내 액티비티 목록 |
| `GET` | `/recommendations/detail/{course_id}/cafes` | 코스 내 카페 목록 |
| `GET` | `/recommendations/detail/{course_id}/restaurants` | 코스 내 식당 목록 |

#### Export Logs

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/api/v1/export-logs` | 코스 내보내기 이벤트 기록 (course_export, course_send, export_close) |

---

### 3-1. 핵심 구현 내용

이 프로젝트는 사용자가 장소·시간·이동수단을 입력하여 맞춤 데이트 코스를 추천받을 수 있도록 구현했습니다.
전체 구조는 프론트엔드 / 백엔드 / DB / 외부 API로 나누어 설계했으며, 주요 데이터 흐름은 다음과 같습니다.

1. 사용자가 장소·시간·이동수단을 입력하고 코스 생성 버튼을 클릭한다.
2. 프론트엔드에서 입력값을 검증한 뒤 서버로 요청을 보낸다.
3. 서버는 요청받은 장소를 DB에서 조회한 후, 추천 코스를 Kakao Map API로 검증하여 반환한다
4. Today Pick 1개 + Sub Course 2개(Course A, Course B)로 구성된 추천 결과를 사용자 화면에 반영한다.

**주요 기능**

- **코스 추천**: 사용자 입력값(장소·시간·이동수단) 기반으로 음식점·카페·활동 유형을 조합한 데이트 코스 3개를 생성
- **코스 상세 조회**: 지도 동선, 장소명·주소·이동 소요시간을 카드 형태로 제공
- **코스 공유**: 코스 상세페이지 링크를 공유하여 다른 사람도 동일한 코스를 확인 가능

### 3-2. 기술적 의사결정

- **FastAPI**: Python 기반 비동기 처리를 지원하며, 자동 API 문서(Swagger)가 생성되어 프론트엔드와의 협업 속도를 높임
- **aiomysql**: FastAPI의 async/await 구조에 맞춰 DB I/O를 비동기로 처리하여 블로킹 없이 다수의 요청을 처리하기 위해 선택
- **Redis**: 동일 지역에 대한 반복적인 장소 검색 API 호출 비용을 줄이기 위해 후보 장소를 캐싱. TTL 2시간을 설정하여 데이터 신선도를 유지
- **Kakao Map API**: 초기에는 네이버 API를 사용했으나 국내 장소 데이터의 정확도와 코스 추천 품질 및 무료 사용량 한도를 고려하여 전환
- **MySQL**: 코스 저장, 이벤트 로그 등 향후 기능 확장을 고려하여 관계형 데이터베이스로 구조화된 데이터를 관리하기 위해 선택
- **Docker + AWS EC2**: 유지보수와 보안성 및 추가 서비스 확장성을 고려하여 AWS EC2를 선택했으며, Docker를 통해 환경에 관계없이 일관된 배포 환경을 구성

### 3-3. 성능 개선

초기 구현에서는 코스 추천 요청마다 Kakao API를 직접 호출하여 응답 속도가 느리고, 품질이 낮은 장소가 추천되는 문제가 있었습니다. 이를 해결하기 위해 다음과 같은 개선을 진행했습니다.

- **Redis 후보 캐시 (TTL 2시간)**: 동일 지역에 대한 반복 API 호출을 캐싱으로 대체하여 응답 속도를 개선하고 불필요한 외부 API 요청을 줄임
- **큐레이션 풀 및 블랙리스트 적용**: 품질이 낮거나 부적절한 장소가 추천되는 문제를 사전 필터링으로 해결하여 추천 결과의 품질을 개선
- **비동기 커넥션 풀**: aiomysql 기반 비동기 DB 연결로 I/O 블로킹을 제거

### 3-4. 테스트

자동화 테스트 없이 로컬 환경에서 직접 API를 호출하여 수동 테스트를 진행했습니다.

- 코스 추천 API 요청 및 응답 정상 동작 여부
- Kakao API 연동 및 장소 검색 결과 정상 반환 여부
- Redis 캐시 적재 및 캐시 히트 동작 여부
- 이벤트 로그 DB 저장 여부 (홈·랜딩·코스·내보내기)
- 필수 입력값 누락 시 예외 처리 동작 여부
- 배포 환경에서 실제 동작 여부

### 3-5. 트러블 슈팅

#### 문제 1. 네이버 API → 카카오 API 전환

- **문제 상황**: 네이버 장소 검색 API 사용 중 국내 장소 데이터의 정확도와 추천 품질에 한계가 있었고, 무료 사용량 한도 문제도 발생
- **해결 방법**: Kakao Map REST API로 전환하여 장소 데이터 품질과 안정적인 API 호출 환경을 확보
- **배운 점**: 외부 API 선택 시 데이터 품질과 사용량 정책을 사전에 충분히 검토해야 한다는 점을 확인

#### 문제 2. 코스 추천 품질 저하

- **문제 상황**: 초기 추천 로직에서 음식점·카페·활동 유형만 단순 조합하여 코스를 구성했고, 스코어 산정 방식이 세밀하게 설계되지 않아 품질이 낮은 장소가 추천되는 문제가 발생
- **원인**: 장소 간 거리·소요시간·사용자 조건을 반영하지 않은 단순 조합 방식
- **해결 방법**: 스코어 산정 로직을 개선하고 큐레이션 풀과 블랙리스트를 도입하여 장소 품질 필터링을 강화
- **배운 점**: 추천 시스템에서 단순 조합보다 품질 기준과 필터링 전략이 중요하다는 것을 확인

### 3-6. 배포

**배포 아키텍처**

```
사용자 → dehangsa.com → Route 53 → CloudFront → EC2 (Docker/Nginx)
                                    (HTTPS 지원)   (Frontend + Backend)
```

**배포 과정**

1. GitHub main 브랜치에 코드를 푸시
2. GitHub Actions가 자동으로 Docker 이미지를 빌드
3. 빌드된 이미지를 GHCR(GitHub Container Registry)에 푸시
4. AWS EC2 서버에서 이미지를 Pull하여 docker-compose로 실행
5. Route 53으로 도메인(dehangsa.com)을 연결하고 CloudFront를 통해 HTTPS 통신 지원
6. 배포 환경에서 실제 동작 여부 확인

배포 후에는 환경변수(.env) 설정을 통해 DB 및 외부 API 연결을 관리

---

### 4-1. 프로젝트 성과

**진행 기간**: 2026-04-01 ~ 진행중

**누적 사용자**: 3,000명

**퍼널 전환율 목표 KPI**

| 지표 | 목표 |
|------|------|
| 랜딩 → 홈 진입 | 35% |
| 코스 생성 | 50% |
| 추천 카드 클릭 | 70% |
| Share 버튼 클릭 | 25% |
| 공유 링크 클릭 | 80% |

**Cycle 1~6** (핵심 퍼널 전환율 측정)

| 지표 | 평균 전환율 |
|------|------------|
| 홈 진입 후 코스 생성률 | 58% (v6에서 80%까지 개선) |
| 추천 코스 카드 클릭 | 86.3% |
| Share 버튼 클릭 | 29% |
| 공유 링크 클릭 | 90.0% |

→ 초기 반응을 위한 지표측정에서는 목표 KPI 에 따른 퍼널 전환율이 비교적 유의미한 결과를 유지, 그렇지만 시장 검증을 위한 사용자 유입이 많지 않아 퍼널 전환율이 안정적이라고 판단하기 어려움.

**Cycle 7** (PMF 가능성 검증, 인스타 광고 유입 이후 핵심 퍼널 전환율 측정)

| 지표 | 평균 전환율 |
|------|------------|
| 랜딩 → 홈 진입 | 36.8% |
| 홈 진입 후 코스 생성 | 86.9% |
| 추천 코스 카드 클릭 | 71% |
| Share 버튼 클릭 | 16.7% |
| 공유 링크 클릭 | 95.0% |

→ 핵심 플로우에 진입한 사용자는 서비스 가치를 경험할 가능성이 높다는 점을 확인, 그렇지만 랜딩페이지에서 홈으로 진입하는 사용자들에서 이탈이 많이 발생하고, Share 버튼 클릭율의 수치가 많이 떨어진 것을 확인하여 개선이 필요.

### 4-2. 배운 점

- 사용자를 관찰하고, 그 안에서 근본적인 문제를 정의하는 과정의 중요성을 체감
- 단순히 기능을 먼저 구현하는 것이 아니라, 사용자가 어떤 상황에서 어떤 불편을 겪는지 파악한 뒤 그 문제를 해결하기 위한 방향으로 의사결정을 진행해야 한다는 점을 상기
- 문제 정의 → 해결 아이디어 도출 → 기능 구현 → 데이터 검증의 흐름으로 프로젝트를 진행하면서, 개발 단계에서도 "진짜 사용자의 문제를 해결하는 기능인가?"라는 관점이 중요하다는 것을 경험

### 4-3. 한계점

- 초기 MVP 단계였기 때문에 추천 코스의 다양성과 상세 정보 제공에 한계가 있었음
- 사용자에게 맞춤형 코스를 추천하는 구조는 구현했지만, 장소 Pool이 충분하지 않아 코스 구성이 제한적이었고, 추천 장소에 대한 이미지와 상세 정보도 부족
- 코스 장소와 무관한 이미지가 노출되는 문제 및 추천 결과의 신뢰도를 높이기 위한 데이터 정제와 이미지 매칭 로직 개선 필요
- 체류시간, 리텐션, Device별 유입 경로를 측정할 수 있는 구조를 초기부터 설계하지 못해 사용자 이탈 구간 및 유입 환경에 대한 세부 분석에 어려움이 있었음

### 4-4. 향후 개선 방향

- Device별 사용자 유입, 체류시간, 리텐션을 측정할 수 있도록 데이터 수집 구조 개선 예정
- 단순 퍼널 전환율뿐 아니라 사용자의 이탈 구간과 반복 사용 가능성을 더 세밀하게 분석하는 것을 목표
- 사용자 입력 카테고리를 세분화하여 맞춤형 코스 추천 정확도를 향상할 계획 (예: 소개팅 첫 만남, 비 오는 날, 실내 데이트, 가성비 데이트 등 상황 기반 조건 반영)
- 코스 장소 Pool을 확장하여 최신 트렌드와 핫플레이스를 반영하고, 추천 장소의 이미지와 상세 정보를 보강
- 광고 배너, 추천 장소 제휴, 쿠폰 제공 등 BM 가능성도 함께 검토 중

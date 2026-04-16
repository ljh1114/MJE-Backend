# MJE-Backend

백엔드 API 프로젝트입니다. **레이어드 아키텍처**를 기본으로 하며, 아래 문서와 Cursor 규칙이 동일한 기준을 공유합니다.

| 문서 / 설정 | 용도 |
|-------------|------|
| 이 `README.md` | 상세 아키텍처·규칙 (단일 기준) |
| [`.cursor/rules/mje-layered-architecture.mdc`](./.cursor/rules/mje-layered-architecture.mdc) | Cursor에서 세션마다 자동 적용되는 동일 규칙 요약 |

소스 트리가 생기면 프로젝트별 폴더 구조(예: `Controllers/`, `Services/`, `Repositories/`, `Entities/`, `DTOs/`)를 이 README의 계층에 맞춰 배치합니다.

---

# Layered Architecture Guide

이 프로젝트는 Layered Architecture를 기본 구조로 사용합니다.

기본 호출 흐름:

Controller -> Service -> Repository

Entity는 특정 계층의 하위 레이어가 아니라,
Service와 Repository에서 함께 사용하는 도메인 모델이다.

---

## Core Rule

- Controller는 요청을 받고 응답을 반환한다.
- Service는 비즈니스 로직과 UseCase를 처리한다.
- Repository는 도메인 객체의 저장 및 조회를 담당한다.
- Entity는 비즈니스 데이터를 표현하며, 필요 시 간단한 규칙을 포함할 수 있다.

---

## Dependency Rule

허용:
- Controller -> Service
- Service -> Repository
- Service -> Entity
- Repository -> Entity

금지:
- Service -> Controller
- Repository -> Service / Controller
- Entity -> Controller / Service / Repository

---

## Layer Responsibilities

### Controller
- 요청 수신
- Request 검증 (DTO)
- Service 호출
- Response DTO 반환
- 상태 코드 및 예외 응답 처리

### Service
- 비즈니스 로직 수행
- UseCase 실행
- 여러 Repository 조합 가능
- 트랜잭션 처리 담당
- 흐름 제어 (orchestration 역할)

### Repository
- DB 등 데이터 저장소에 직접 접근하는 계층이다.
- Entity의 저장, 조회, 수정, 삭제를 담당한다.
- 내부적으로 ORM/SQL 등 데이터 접근에 필요한 세부 구현을 담당한다.
- Service가 비즈니스 로직에 집중할 수 있도록 데이터 접근 로직을 캡슐화한다.

### Entity
- 비즈니스 데이터와 상태를 표현한다.
- 자신의 데이터와 직접 관련된 규칙만 포함할 수 있다.
- 흐름 제어, DB 접근, 외부 API 호출은 포함하지 않는다.
- 다른 계층을 참조하지 않는다.

---

## DTO and Entity Rule

- Request/Response는 DTO를 사용한다.
- Entity는 내부 도메인 모델로 사용한다.
- Controller는 Entity를 직접 반환하지 않는다.
- API 응답은 반드시 Response DTO로 변환하여 반환한다.

---

## Transaction Rule

- 트랜잭션 경계는 Service에서 관리한다.
- Repository는 개별 DB 작업만 수행한다.
- 여러 Repository 작업을 하나의 비즈니스 로직으로 묶을 때 Service에서 처리한다.

---

## Exception Handling Rule

- Repository는 DB/ORM 관련 예외를 발생시킬 수 있다.
- Service는 이를 비즈니스 예외로 변환할 수 있다.
- Controller는 비즈니스 예외를 HTTP 응답으로 변환한다.
- 내부 예외(DB, ORM 등)를 그대로 외부에 노출하지 않는다.

---

## Service and Entity Rule

- Service는 유스케이스 흐름 제어를 담당한다.
- Service는 여러 Repository와 Entity를 조합하여 로직을 수행한다.
- Entity는 비즈니스 데이터와 상태를 표현한다.
- Entity는 자신의 상태와 직접 관련된 규칙만 표현한다.
- 상태 변경을 수행하는 처리 흐름은 Service에 둔다.
- DB 접근, 외부 API 호출, 여러 객체를 조합한 처리 로직은 Service에 둔다.

---

## Anti-Patterns

- Controller에 비즈니스 로직 작성 금지
- Service에서 DB 직접 접근 금지
- Repository에 비즈니스 정책 작성 금지
- Entity에서 외부 의존성 사용 금지
- Entity를 API Response로 직접 반환 금지

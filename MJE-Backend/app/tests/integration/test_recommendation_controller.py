from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_recommendation_returns_main_and_secondary_courses() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "강남",
            "time_slot": "저녁",
            "activity_type": "식사",
            "transportation": "자차",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["request_condition"] == {
        "place": "gangnam",
        "time_slot": "evening",
        "activity_type": "dining",
        "transportation": "car",
    }
    assert payload["summary"] == {
        "total_courses": 3,
        "main_course_count": 1,
        "secondary_course_count": 2,
    }
    assert payload["main_course"]["place_name"] == "강남 와인 다이닝 거리"
    assert "keywords" in payload["main_course"]
    assert len(payload["secondary_courses"]) == 2
    assert len(payload["courses"]) == 3
    assert payload["courses"][0]["course_type"] == "main"


def test_create_recommendation_returns_rule_based_course_for_car_activity() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "홍대",
            "time_slot": "evening",
            "activity_type": "activity",
            "transportation": "car",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["main_course"]["title"] == "홍대 액티비티 드라이브 데이트"
    assert payload["secondary_courses"][0]["course_type"] == "secondary"
    assert payload["summary"]["total_courses"] == 3


def test_create_recommendation_returns_error_for_invalid_input() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "busan",
            "time_slot": "저녁",
            "activity_type": "식사",
            "transportation": "자차",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RECOMMENDATION_INVALID_INPUT"
    assert response.json()["detail"]["field"] == "place"
    assert response.json()["detail"]["invalid_value"] == "busan"
    assert "gangnam" in response.json()["detail"]["allowed_values"]


def test_create_recommendation_returns_error_for_invalid_request_payload() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "강남",
            "time_slot": "저녁",
            "activity_type": "식사",
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "RECOMMENDATION_INVALID_REQUEST"
    assert response.json()["field"] == "transportation"


def test_create_recommendation_returns_error_when_rule_not_matched() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "홍대",
            "time_slot": "밤",
            "activity_type": "액티비티",
            "transportation": "대중교통",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RECOMMENDATION_RULE_NOT_MATCHED"
    assert response.json()["detail"]["field"] is None

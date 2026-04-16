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
    assert payload["main_course"]["place_name"] == "강남 와인 다이닝 거리"
    assert "keywords" in payload["main_course"]
    assert len(payload["secondary_courses"]) == 2


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


def test_create_recommendation_returns_error_when_rule_not_matched() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "강남",
            "time_slot": "아침",
            "activity_type": "액티비티",
            "transportation": "자차",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RECOMMENDATION_RULE_NOT_MATCHED"

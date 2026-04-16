from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_recommendation_returns_main_and_secondary_courses() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "gangnam",
            "time_slot": "evening",
            "activity_type": "dining",
            "transportation": "car",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["main_course"]["place_name"] == "강남 와인 다이닝 거리"
    assert "keywords" in payload["main_course"]
    assert len(payload["secondary_courses"]) == 2


def test_create_recommendation_returns_error_when_rule_not_matched() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "place": "gangnam",
            "time_slot": "morning",
            "activity_type": "activity",
            "transportation": "car",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RECOMMENDATION_RULE_NOT_MATCHED"

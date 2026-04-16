import pytest

from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationInvalidInputError,
    RecommendationRuleNotMatchedError,
)
from app.domains.recommendation.services.recommendation_service import (
    RecommendationService,
)


def test_generate_recommendation_creates_expected_shape() -> None:
    service = RecommendationService()

    result = service.generate_recommendation(
        RecommendationRequest(
            place="seongsu",
            time_slot="afternoon",
            activity_type="cafe",
            transportation="public_transport",
        )
    )

    assert result.main_course.course_type == "main"
    assert len(result.secondary_courses) == 2
    assert all(course.keywords for course in result.secondary_courses)


def test_interpret_condition_normalizes_alias_values() -> None:
    service = RecommendationService()

    condition = service.interpret_condition(
        RecommendationRequest(
            place=" 강남 ",
            time_slot="저녁",
            activity_type="식사",
            transportation="자차",
        )
    )

    assert condition.place == "gangnam"
    assert condition.time_slot == "evening"
    assert condition.activity_type == "dining"
    assert condition.transportation == "car"


def test_interpret_condition_raises_for_invalid_value() -> None:
    service = RecommendationService()

    with pytest.raises(RecommendationInvalidInputError) as error:
        service.interpret_condition(
            RecommendationRequest(
                place="busan",
                time_slot="evening",
                activity_type="dining",
                transportation="car",
            )
        )

    assert error.value.field_name == "place"


def test_generate_recommendation_raises_for_unmatched_rule() -> None:
    service = RecommendationService()

    with pytest.raises(RecommendationRuleNotMatchedError):
        service.generate_recommendation(
            RecommendationRequest(
                place="jamsil",
                time_slot="night",
                activity_type="dining",
                transportation="car",
            )
        )

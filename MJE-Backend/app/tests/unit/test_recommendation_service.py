import pytest

from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.exceptions.recommendation_exceptions import (
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

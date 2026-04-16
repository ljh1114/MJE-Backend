import pytest

from app.domains.recommendation.dtos.recommendation_course_detail_request import (
    RecommendationCourseDetailRequest,
)
from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)
from app.domains.recommendation.entities.course_detail import CourseDetail
from app.domains.recommendation.entities.course_detail_item import CourseDetailItem
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationCourseIdentifierError,
    RecommendationCourseIdentifierFormatError,
    RecommendationInvalidCourseResultError,
    RecommendationInvalidInputError,
    RecommendationRuleNotMatchedError,
)
from app.domains.recommendation.services.recommendation_rule_engine import (
    RecommendationRuleEngine,
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

    assert result.condition.place == "seongsu"
    assert result.condition.time_slot == "afternoon"
    assert result.main_course.course_type == "main"
    assert len(result.secondary_courses) == 2
    assert all(course.keywords for course in result.secondary_courses)


def test_rule_engine_matches_rule_from_condition() -> None:
    rule_engine = RecommendationRuleEngine()

    rule = rule_engine.match_rule(
        RecommendationCondition(
            place="gangnam",
            time_slot="evening",
            activity_type="dining",
            transportation="car",
        )
    )

    assert rule.rule_name == "gangnam_evening_dining_car"
    assert rule.main_course_template.place_name == "강남 와인 다이닝 거리"


def test_rule_engine_blocks_exceptional_night_public_transport_case() -> None:
    rule_engine = RecommendationRuleEngine()

    with pytest.raises(RecommendationRuleNotMatchedError) as error:
        rule_engine.match_rule(
            RecommendationCondition(
                place="hongdae",
                time_slot="night",
                activity_type="activity",
                transportation="public_transport",
            )
        )

    assert "Late-night" in str(error.value)


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


def test_get_course_detail_returns_detail_list() -> None:
    service = RecommendationService()

    result = service.get_course_detail("course-seongsu-main")

    assert result.course_id == "course-seongsu-main"
    assert result.recommendation_id == "recommendation-template-seongsu-main"
    assert result.condition.place == "seongsu"
    assert len(result.detail_items) == 3
    assert result.detail_items[0].sequence == 1
    assert result.detail_items[0].component_type == "cafe"


def test_validate_course_detail_request_returns_normalized_identifier() -> None:
    service = RecommendationService()

    result = service.validate_course_detail_request(
        RecommendationCourseDetailRequest(course_id=" COURSE-GANGNAM-MAIN ")
    )

    assert result == "course-gangnam-main"


def test_validate_course_detail_request_raises_for_invalid_format() -> None:
    service = RecommendationService()

    with pytest.raises(RecommendationCourseIdentifierFormatError):
        service.validate_course_detail_request(
            RecommendationCourseDetailRequest(course_id="gangnam-main")
        )


def test_get_course_detail_raises_for_invalid_identifier() -> None:
    service = RecommendationService()

    with pytest.raises(RecommendationCourseIdentifierError):
        service.get_course_detail("invalid-course-id")


def test_get_course_detail_raises_for_invalid_course_result() -> None:
    service = RecommendationService()
    service._COURSE_DETAILS["course-invalid-main"] = CourseDetail(
        course_id="course-invalid-main",
        course_title="비정상 코스",
        recommendation_id="recommendation-template-invalid-main",
        condition=RecommendationCondition(
            place="gangnam",
            time_slot="evening",
            activity_type="dining",
            transportation="car",
        ),
        detail_items=[
            CourseDetailItem(
                sequence=1,
                component_type="restaurant",
                name="테스트 식당",
                description="식당만 있는 비정상 데이터",
                keywords=["테스트"],
            )
        ],
    )

    with pytest.raises(RecommendationInvalidCourseResultError):
        service.get_course_detail("course-invalid-main")

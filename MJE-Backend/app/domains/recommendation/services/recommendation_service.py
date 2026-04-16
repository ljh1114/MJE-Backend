from uuid import uuid4

from app.domains.recommendation.entities.course_detail import CourseDetail
from app.domains.recommendation.entities.course_detail_item import CourseDetailItem
from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)
from app.domains.recommendation.entities.recommendation import Recommendation
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationCourseIdentifierError,
    RecommendationInvalidInputError,
)
from app.domains.recommendation.services.recommendation_rule_engine import (
    RecommendationRuleEngine,
)


class RecommendationService:
    """Use-case orchestration for recommendation domain."""

    _COURSE_DETAILS: dict[str, CourseDetail] = {
        "course-gangnam-main": CourseDetail(
            course_id="course-gangnam-main",
            course_title="강남 감성 다이닝 데이트",
            recommendation_id="recommendation-template-gangnam-main",
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
                    name="강남 와인 다이닝",
                    description="분위기 있는 저녁 식사를 즐길 수 있는 메인 식당 코스",
                    keywords=["와인", "저녁식사", "분위기"],
                ),
                CourseDetailItem(
                    sequence=2,
                    component_type="cafe",
                    name="강남 루프탑 카페",
                    description="식사 후 야경과 디저트를 즐길 수 있는 카페 코스",
                    keywords=["야경", "디저트", "대화"],
                ),
                CourseDetailItem(
                    sequence=3,
                    component_type="activity",
                    name="반포한강공원 산책",
                    description="데이트 마무리로 가볍게 산책할 수 있는 활동 코스",
                    keywords=["산책", "야경", "드라이브"],
                ),
            ],
        ),
        "course-seongsu-main": CourseDetail(
            course_id="course-seongsu-main",
            course_title="성수 카페 투어 데이트",
            recommendation_id="recommendation-template-seongsu-main",
            condition=RecommendationCondition(
                place="seongsu",
                time_slot="afternoon",
                activity_type="cafe",
                transportation="public_transport",
            ),
            detail_items=[
                CourseDetailItem(
                    sequence=1,
                    component_type="cafe",
                    name="성수 시그니처 카페",
                    description="감성적인 인테리어와 디저트가 있는 메인 카페 코스",
                    keywords=["카페투어", "감성", "사진"],
                ),
                CourseDetailItem(
                    sequence=2,
                    component_type="activity",
                    name="성수 편집숍 투어",
                    description="트렌디한 브랜드와 팝업을 둘러보는 활동 코스",
                    keywords=["쇼핑", "팝업", "도보"],
                ),
                CourseDetailItem(
                    sequence=3,
                    component_type="restaurant",
                    name="서울숲 브런치 식당",
                    description="가볍게 식사할 수 있는 브런치 중심 식당 코스",
                    keywords=["브런치", "휴식", "서울숲"],
                ),
            ],
        ),
        "course-hongdae-main": CourseDetail(
            course_id="course-hongdae-main",
            course_title="홍대 액티비티 드라이브 데이트",
            recommendation_id="recommendation-template-hongdae-main",
            condition=RecommendationCondition(
                place="hongdae",
                time_slot="evening",
                activity_type="activity",
                transportation="car",
            ),
            detail_items=[
                CourseDetailItem(
                    sequence=1,
                    component_type="activity",
                    name="홍대 복합 액티비티 존",
                    description="실내 체험과 게임을 즐길 수 있는 메인 활동 코스",
                    keywords=["체험", "게임", "활동"],
                ),
                CourseDetailItem(
                    sequence=2,
                    component_type="cafe",
                    name="연남 디저트 카페",
                    description="체험 후 달콤한 디저트를 즐기는 카페 코스",
                    keywords=["디저트", "휴식", "감성"],
                ),
                CourseDetailItem(
                    sequence=3,
                    component_type="restaurant",
                    name="망원 야경 레스토랑",
                    description="드라이브 후 식사하며 마무리하는 식당 코스",
                    keywords=["야경", "식사", "마무리"],
                ),
            ],
        ),
        "course-jamsil-main": CourseDetail(
            course_id="course-jamsil-main",
            course_title="잠실 아침 산책 데이트",
            recommendation_id="recommendation-template-jamsil-main",
            condition=RecommendationCondition(
                place="jamsil",
                time_slot="morning",
                activity_type="walk",
                transportation="public_transport",
            ),
            detail_items=[
                CourseDetailItem(
                    sequence=1,
                    component_type="activity",
                    name="석촌호수 산책",
                    description="아침 공기를 즐기며 여유롭게 걷는 메인 활동 코스",
                    keywords=["산책", "호수뷰", "여유"],
                ),
                CourseDetailItem(
                    sequence=2,
                    component_type="cafe",
                    name="송리단길 브런치 카페",
                    description="산책 후 가볍게 브런치를 즐길 수 있는 카페 코스",
                    keywords=["브런치", "대화", "가벼움"],
                ),
                CourseDetailItem(
                    sequence=3,
                    component_type="restaurant",
                    name="잠실 캐주얼 다이닝",
                    description="전시 전후로 식사하기 좋은 식당 코스",
                    keywords=["실내", "식사", "문화"],
                ),
            ],
        ),
    }

    _PLACE_ALIASES = {
        "gangnam": "gangnam",
        "강남": "gangnam",
        "seongsu": "seongsu",
        "성수": "seongsu",
        "hongdae": "hongdae",
        "홍대": "hongdae",
        "jamsil": "jamsil",
        "잠실": "jamsil",
    }
    _TIME_SLOT_ALIASES = {
        "morning": "morning",
        "아침": "morning",
        "afternoon": "afternoon",
        "오후": "afternoon",
        "evening": "evening",
        "저녁": "evening",
        "night": "night",
        "밤": "night",
    }
    _ACTIVITY_TYPE_ALIASES = {
        "cafe": "cafe",
        "카페": "cafe",
        "culture": "culture",
        "문화": "culture",
        "activity": "activity",
        "액티비티": "activity",
        "walk": "walk",
        "산책": "walk",
        "dining": "dining",
        "식사": "dining",
    }
    _TRANSPORTATION_ALIASES = {
        "car": "car",
        "자차": "car",
        "public_transport": "public_transport",
        "대중교통": "public_transport",
    }

    def __init__(self) -> None:
        self._rule_engine = RecommendationRuleEngine()

    def interpret_condition(
        self, request: RecommendationRequest
    ) -> RecommendationCondition:
        return RecommendationCondition(
            place=self._normalize_value(
                field_name="place",
                raw_value=request.place,
                aliases=self._PLACE_ALIASES,
            ),
            time_slot=self._normalize_value(
                field_name="time_slot",
                raw_value=request.time_slot,
                aliases=self._TIME_SLOT_ALIASES,
            ),
            activity_type=self._normalize_value(
                field_name="activity_type",
                raw_value=request.activity_type,
                aliases=self._ACTIVITY_TYPE_ALIASES,
            ),
            transportation=self._normalize_value(
                field_name="transportation",
                raw_value=request.transportation,
                aliases=self._TRANSPORTATION_ALIASES,
            ),
        )

    def generate_recommendation(
        self, request: RecommendationRequest
    ) -> Recommendation:
        condition = self.interpret_condition(request)
        matched_rule = self._rule_engine.match_rule(condition)
        return self._rule_engine.compose_recommendation(
            recommendation_id=str(uuid4()),
            rule=matched_rule,
        )

    def get_course_detail(self, course_id: str) -> CourseDetail:
        normalized_course_id = course_id.strip()
        course_detail = self._COURSE_DETAILS.get(normalized_course_id)
        if course_detail is None:
            raise RecommendationCourseIdentifierError(course_id=course_id)
        return course_detail

    def _normalize_value(
        self, field_name: str, raw_value: str, aliases: dict[str, str]
    ) -> str:
        normalized = raw_value.strip().lower()
        matched_value = aliases.get(normalized)
        if matched_value is not None:
            return matched_value

        stripped_value = raw_value.strip()
        matched_value = aliases.get(stripped_value)
        if matched_value is not None:
            return matched_value

        raise RecommendationInvalidInputError(
            field_name=field_name,
            field_value=raw_value,
            allowed_values=sorted(set(aliases.values())),
        )

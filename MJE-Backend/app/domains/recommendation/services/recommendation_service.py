from uuid import uuid4

from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.entities.course import Course
from app.domains.recommendation.entities.recommendation import Recommendation
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationRuleNotMatchedError,
)


class RecommendationService:
    """Use-case orchestration for recommendation domain."""

    _RULES: dict[tuple[str, str, str, str], Recommendation] = {
        (
            "gangnam",
            "evening",
            "dining",
            "car",
        ): Recommendation(
            recommendation_id="template-gangnam-evening-dining-car",
            main_course=Course(
                course_type="main",
                title="강남 감성 다이닝 데이트",
                place_name="강남 와인 다이닝 거리",
                keywords=["와인", "분위기", "저녁식사"],
            ),
            secondary_courses=[
                Course(
                    course_type="secondary",
                    title="루프탑 카페 마무리 코스",
                    place_name="강남 루프탑 카페",
                    keywords=["야경", "디저트", "대화"],
                ),
                Course(
                    course_type="secondary",
                    title="한강 드라이브 산책 코스",
                    place_name="반포한강공원",
                    keywords=["드라이브", "산책", "야경"],
                ),
            ],
        ),
        (
            "seongsu",
            "afternoon",
            "cafe",
            "public_transport",
        ): Recommendation(
            recommendation_id="template-seongsu-afternoon-cafe-public-transport",
            main_course=Course(
                course_type="main",
                title="성수 카페 투어 데이트",
                place_name="성수 연무장길",
                keywords=["카페투어", "감성", "사진"],
            ),
            secondary_courses=[
                Course(
                    course_type="secondary",
                    title="성수 편집숍 산책 코스",
                    place_name="성수동 팝업 거리",
                    keywords=["쇼핑", "트렌디", "도보"],
                ),
                Course(
                    course_type="secondary",
                    title="서울숲 여유 코스",
                    place_name="서울숲",
                    keywords=["휴식", "산책", "자연"],
                ),
            ],
        ),
        (
            "hongdae",
            "night",
            "activity",
            "public_transport",
        ): Recommendation(
            recommendation_id="template-hongdae-night-activity-public-transport",
            main_course=Course(
                course_type="main",
                title="홍대 액티비티 나이트 데이트",
                place_name="홍대 놀거리 거리",
                keywords=["체험", "활동", "야간"],
            ),
            secondary_courses=[
                Course(
                    course_type="secondary",
                    title="보드게임 카페 코스",
                    place_name="홍대 보드게임 카페",
                    keywords=["실내", "게임", "친밀감"],
                ),
                Course(
                    course_type="secondary",
                    title="심야 디저트 코스",
                    place_name="연남동 디저트 거리",
                    keywords=["디저트", "심야", "도보"],
                ),
            ],
        ),
        (
            "jamsil",
            "morning",
            "walk",
            "public_transport",
        ): Recommendation(
            recommendation_id="template-jamsil-morning-walk-public-transport",
            main_course=Course(
                course_type="main",
                title="잠실 아침 산책 데이트",
                place_name="석촌호수",
                keywords=["산책", "여유", "호수뷰"],
            ),
            secondary_courses=[
                Course(
                    course_type="secondary",
                    title="브런치 카페 코스",
                    place_name="송리단길 브런치 카페",
                    keywords=["브런치", "대화", "가벼움"],
                ),
                Course(
                    course_type="secondary",
                    title="전시 관람 코스",
                    place_name="롯데월드몰 문화 공간",
                    keywords=["전시", "실내", "문화"],
                ),
            ],
        ),
    }

    def generate_recommendation(
        self, request: RecommendationRequest
    ) -> Recommendation:
        rule_key = (
            request.place,
            request.time_slot,
            request.activity_type,
            request.transportation,
        )
        recommendation = self._RULES.get(rule_key)
        if recommendation is None:
            raise RecommendationRuleNotMatchedError(
                "No recommendation rule matched the given input."
            )

        return Recommendation(
            recommendation_id=str(uuid4()),
            main_course=recommendation.main_course,
            secondary_courses=recommendation.secondary_courses,
        )

from app.domains.recommendation.entities.course import Course
from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)
from app.domains.recommendation.entities.recommendation_rule import RecommendationRule
from app.domains.recommendation.entities.recommendation import Recommendation
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationRuleNotMatchedError,
)


class RecommendationRuleEngine:
    """Matches normalized conditions to recommendation rules."""

    def __init__(self) -> None:
        self._rules = self._build_rules()

    def match_rule(self, condition: RecommendationCondition) -> RecommendationRule:
        self._validate_exceptional_condition(condition)

        for rule in self._rules:
            if rule.condition == condition:
                return rule

        raise RecommendationRuleNotMatchedError(
            "No recommendation rule matched the given input."
        )

    def compose_recommendation(
        self, recommendation_id: str, rule: RecommendationRule
    ) -> Recommendation:
        main_course = Course(
            course_type="main",
            title=rule.main_course_template.title,
            place_name=rule.main_course_template.place_name,
            keywords=rule.main_course_template.keywords,
        )
        secondary_courses = [
            Course(
                course_type="secondary",
                title=course.title,
                place_name=course.place_name,
                keywords=course.keywords,
            )
            for course in rule.secondary_course_templates
        ]
        return Recommendation(
            recommendation_id=recommendation_id,
            condition=rule.condition,
            main_course=main_course,
            secondary_courses=secondary_courses,
        )

    def _validate_exceptional_condition(
        self, condition: RecommendationCondition
    ) -> None:
        if condition.time_slot == "night" and condition.transportation == "public_transport":
            raise RecommendationRuleNotMatchedError(
                "Late-night recommendations with public transport are not supported yet."
            )

    def _build_rules(self) -> list[RecommendationRule]:
        return [
            RecommendationRule(
                rule_name="gangnam_evening_dining_car",
                condition=RecommendationCondition(
                    place="gangnam",
                    time_slot="evening",
                    activity_type="dining",
                    transportation="car",
                ),
                main_course_template=Course(
                    course_type="main",
                    title="강남 감성 다이닝 데이트",
                    place_name="강남 와인 다이닝 거리",
                    keywords=["와인", "분위기", "저녁식사"],
                ),
                secondary_course_templates=[
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
            RecommendationRule(
                rule_name="seongsu_afternoon_cafe_public_transport",
                condition=RecommendationCondition(
                    place="seongsu",
                    time_slot="afternoon",
                    activity_type="cafe",
                    transportation="public_transport",
                ),
                main_course_template=Course(
                    course_type="main",
                    title="성수 카페 투어 데이트",
                    place_name="성수 연무장길",
                    keywords=["카페투어", "감성", "사진"],
                ),
                secondary_course_templates=[
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
            RecommendationRule(
                rule_name="jamsil_morning_walk_public_transport",
                condition=RecommendationCondition(
                    place="jamsil",
                    time_slot="morning",
                    activity_type="walk",
                    transportation="public_transport",
                ),
                main_course_template=Course(
                    course_type="main",
                    title="잠실 아침 산책 데이트",
                    place_name="석촌호수",
                    keywords=["산책", "여유", "호수뷰"],
                ),
                secondary_course_templates=[
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
            RecommendationRule(
                rule_name="hongdae_evening_activity_car",
                condition=RecommendationCondition(
                    place="hongdae",
                    time_slot="evening",
                    activity_type="activity",
                    transportation="car",
                ),
                main_course_template=Course(
                    course_type="main",
                    title="홍대 액티비티 드라이브 데이트",
                    place_name="홍대 복합 놀거리 존",
                    keywords=["체험", "활동", "드라이브"],
                ),
                secondary_course_templates=[
                    Course(
                        course_type="secondary",
                        title="연남동 디저트 코스",
                        place_name="연남동 디저트 거리",
                        keywords=["디저트", "휴식", "감성"],
                    ),
                    Course(
                        course_type="secondary",
                        title="한강 야경 코스",
                        place_name="망원한강공원",
                        keywords=["야경", "산책", "마무리"],
                    ),
                ],
            ),
        ]

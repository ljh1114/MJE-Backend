from uuid import uuid4

from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.entities.recommendation_condition import (
    RecommendationCondition,
)
from app.domains.recommendation.entities.recommendation import Recommendation
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationInvalidInputError,
)
from app.domains.recommendation.services.recommendation_rule_engine import (
    RecommendationRuleEngine,
)


class RecommendationService:
    """Use-case orchestration for recommendation domain."""

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

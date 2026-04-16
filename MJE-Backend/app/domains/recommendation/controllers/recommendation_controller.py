from fastapi import APIRouter, HTTPException, status

from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.dtos.recommendation_response import (
    CourseItemResponse,
    RecommendationConditionResponse,
    RecommendationResponse,
    RecommendationSummaryResponse,
)
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationInvalidInputError,
    RecommendationRuleNotMatchedError,
)
from app.domains.recommendation.services.recommendation_service import (
    RecommendationService,
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendation"])
recommendation_service = RecommendationService()


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def create_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:
    try:
        recommendation = recommendation_service.generate_recommendation(request)
    except RecommendationInvalidInputError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "RECOMMENDATION_INVALID_INPUT",
                "message": str(error),
                "field": error.field_name,
                "allowed_values": error.allowed_values,
            },
        ) from error
    except RecommendationRuleNotMatchedError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "RECOMMENDATION_RULE_NOT_MATCHED",
                "message": str(error),
            },
        ) from error

    secondary_courses = [
        CourseItemResponse(
            course_type=course.course_type,
            title=course.title,
            place_name=course.place_name,
            keywords=course.keywords,
        )
        for course in recommendation.secondary_courses
    ]
    main_course = CourseItemResponse(
        course_type=recommendation.main_course.course_type,
        title=recommendation.main_course.title,
        place_name=recommendation.main_course.place_name,
        keywords=recommendation.main_course.keywords,
    )

    return RecommendationResponse(
        recommendation_id=recommendation.recommendation_id,
        request_condition=RecommendationConditionResponse(
            place=recommendation.condition.place,
            time_slot=recommendation.condition.time_slot,
            activity_type=recommendation.condition.activity_type,
            transportation=recommendation.condition.transportation,
        ),
        summary=RecommendationSummaryResponse(
            total_courses=1 + len(secondary_courses),
            main_course_count=1,
            secondary_course_count=len(secondary_courses),
        ),
        main_course=main_course,
        secondary_courses=secondary_courses,
        courses=[main_course, *secondary_courses],
    )

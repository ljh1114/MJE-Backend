from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.domains.recommendation.dtos.recommendation_course_detail_request import (
    RecommendationCourseDetailRequest,
)
from app.domains.recommendation.dtos.recommendation_error_response import (
    RecommendationErrorResponse,
)
from app.domains.recommendation.dtos.recommendation_course_detail_response import (
    CourseDetailItemResponse,
    RecommendationCourseDetailConditionResponse,
    RecommendationCourseDetailResponse,
    RecommendationCourseDetailSummaryResponse,
)
from app.domains.recommendation.dtos.recommendation_request import RecommendationRequest
from app.domains.recommendation.dtos.recommendation_response import (
    CourseItemResponse,
    RecommendationConditionResponse,
    RecommendationResponse,
    RecommendationSummaryResponse,
)
from app.domains.recommendation.exceptions.recommendation_exceptions import (
    RecommendationCourseIdentifierError,
    RecommendationCourseIdentifierFormatError,
    RecommendationInvalidInputError,
    RecommendationRuleNotMatchedError,
)
from app.domains.recommendation.services.recommendation_service import (
    RecommendationService,
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendation"])
recommendation_service = RecommendationService()


@router.post(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": RecommendationErrorResponse},
    },
)
def create_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:
    try:
        recommendation = recommendation_service.generate_recommendation(request)
    except RecommendationInvalidInputError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RecommendationErrorResponse(
                code=error.error_code,
                message=str(error),
                field=error.field_name,
                invalid_value=error.field_value,
                allowed_values=error.allowed_values,
            ).model_dump(),
        ) from error
    except RecommendationRuleNotMatchedError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RecommendationErrorResponse(
                code="RECOMMENDATION_RULE_NOT_MATCHED",
                message=str(error),
            ).model_dump(),
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


@router.get(
    "/courses/{course_id}/details",
    response_model=RecommendationCourseDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": RecommendationErrorResponse},
    },
)
def get_recommendation_course_detail(
    course_id: str,
) -> RecommendationCourseDetailResponse:
    try:
        request = RecommendationCourseDetailRequest(course_id=course_id)
        normalized_course_id = recommendation_service.validate_course_detail_request(
            request
        )
        course_detail = recommendation_service.get_course_detail(normalized_course_id)
    except ValidationError as error:
        first_error = error.errors()[0]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RecommendationErrorResponse(
                code="RECOMMENDATION_COURSE_IDENTIFIER_INVALID_REQUEST",
                message="Recommendation course detail request is invalid.",
                field="course_id",
                invalid_value=str(first_error.get("input", course_id)),
            ).model_dump(),
        ) from error
    except RecommendationCourseIdentifierFormatError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RecommendationErrorResponse(
                code=error.error_code,
                message=str(error),
                field="course_id",
                invalid_value=error.course_id,
            ).model_dump(),
        ) from error
    except RecommendationCourseIdentifierError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RecommendationErrorResponse(
                code=error.error_code,
                message=str(error),
                field="course_id",
                invalid_value=error.course_id,
            ).model_dump(),
        ) from error

    detail_items = [
        CourseDetailItemResponse(
            sequence=item.sequence,
            component_type=item.component_type,
            name=item.name,
            description=item.description,
            keywords=item.keywords,
        )
        for item in course_detail.detail_items
    ]

    return RecommendationCourseDetailResponse(
        recommendation_id=course_detail.recommendation_id,
        course_id=course_detail.course_id,
        course_title=course_detail.course_title,
        request_condition=RecommendationCourseDetailConditionResponse(
            place=course_detail.condition.place,
            time_slot=course_detail.condition.time_slot,
            activity_type=course_detail.condition.activity_type,
            transportation=course_detail.condition.transportation,
        ),
        summary=RecommendationCourseDetailSummaryResponse(
            total_detail_items=len(detail_items),
            restaurant_count=sum(
                1 for item in detail_items if item.component_type == "restaurant"
            ),
            cafe_count=sum(
                1 for item in detail_items if item.component_type == "cafe"
            ),
            activity_count=sum(
                1 for item in detail_items if item.component_type == "activity"
            ),
        ),
        detail_items=detail_items,
    )

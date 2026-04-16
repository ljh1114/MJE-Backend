from uuid import uuid4

from app.domains.saved_course.dtos.send_saved_course_email_request import (
    SendSavedCourseEmailRequest,
)
from app.domains.saved_course.dtos.send_saved_course_email_response import (
    SendSavedCourseEmailResponse,
)
from app.domains.saved_course.services.email_sender import EmailSender
from app.domains.recommendation.services.recommendation_service import (
    RecommendationService,
)


class SavedCourseService:
    """Use-case orchestration for saved course domain."""

    def create_email_send_request(
        self, request: SendSavedCourseEmailRequest
    ) -> SendSavedCourseEmailResponse:
        request_id = str(uuid4())

        recommendation_service = RecommendationService()
        course_detail = recommendation_service.get_course_detail(request.course_id)

        place_display = self._place_to_display(course_detail.condition.place)
        keywords = self._extract_keywords(
            [keyword for item in course_detail.detail_items for keyword in item.keywords]
        )

        subject_keyword = keywords[0] if keywords else "데이트코스"
        subject = f"[{self._service_name()}] {place_display} {subject_keyword}"

        html_body, text_body = self._build_ticket_email_body(course_detail)

        sender = EmailSender()
        send_result = sender.send(
            to_email=str(request.recipient_email),
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

        if not send_result.success:
            return SendSavedCourseEmailResponse(
                request_id=request_id,
                status="failed",
                recipient_email=str(request.recipient_email),
                course_id=request.course_id,
                course_title=request.course_title,
                failure_reason=send_result.error_message,
            )

        return SendSavedCourseEmailResponse(
            request_id=request_id,
            status="sent",
            recipient_email=str(request.recipient_email),
            course_id=request.course_id,
            course_title=request.course_title,
        )

    def _service_name(self) -> str:
        return "MJE"

    def _place_to_display(self, place: str) -> str:
        return {
            "gangnam": "강남",
            "seongsu": "성수",
            "hongdae": "홍대",
            "jamsil": "잠실",
        }.get(place, place)

    def _extract_keywords(self, keywords: list[str]) -> list[str]:
        unique_keywords: list[str] = []
        for keyword in keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        return unique_keywords[:5]

    def _build_ticket_email_body(self, course_detail) -> tuple[str, str]:
        rows_html = []
        rows_text = []
        for item in sorted(course_detail.detail_items, key=lambda x: x.sequence):
            badge = item.component_type.upper()
            rows_html.append(
                f"""
                <tr>
                  <td style="padding:10px 12px;border-bottom:1px solid #eee;font-size:12px;color:#666;">{item.sequence}</td>
                  <td style="padding:10px 12px;border-bottom:1px solid #eee;">
                    <div style="font-size:12px;color:#999;margin-bottom:4px;">{badge}</div>
                    <div style="font-size:14px;color:#111;font-weight:600;">{item.name}</div>
                    <div style="font-size:12px;color:#444;line-height:1.4;margin-top:6px;">{item.description}</div>
                    <div style="font-size:12px;color:#666;margin-top:6px;">#{' #'.join(item.keywords)}</div>
                  </td>
                </tr>
                """
            )
            rows_text.append(
                f"{item.sequence}. [{badge}] {item.name}\n"
                f"   - {item.description}\n"
                f"   - keywords: {', '.join(item.keywords)}\n"
            )

        condition = course_detail.condition
        condition_text = (
            f"place={condition.place}, time_slot={condition.time_slot}, "
            f"activity_type={condition.activity_type}, transportation={condition.transportation}"
        )

        html = f"""
        <div style="font-family:Arial, Helvetica, sans-serif;background:#f6f7fb;padding:24px;">
          <div style="max-width:720px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e8e8ef;">
            <div style="background:#111827;color:#fff;padding:18px 20px;">
              <div style="font-size:12px;opacity:.85;">MJE DATE COURSE E-TICKET</div>
              <div style="font-size:18px;font-weight:700;margin-top:6px;">{course_detail.course_title}</div>
              <div style="font-size:12px;opacity:.9;margin-top:8px;">COURSE ID: {course_detail.course_id}</div>
            </div>
            <div style="padding:18px 20px;">
              <div style="font-size:12px;color:#6b7280;">REQUEST CONDITION</div>
              <div style="margin-top:6px;font-size:13px;color:#111827;">{condition_text}</div>
            </div>
            <table style="width:100%;border-collapse:collapse;">
              <thead>
                <tr>
                  <th style="text-align:left;padding:10px 12px;background:#f3f4f6;font-size:12px;color:#6b7280;width:52px;">SEQ</th>
                  <th style="text-align:left;padding:10px 12px;background:#f3f4f6;font-size:12px;color:#6b7280;">DETAILS</th>
                </tr>
              </thead>
              <tbody>
                {''.join(rows_html)}
              </tbody>
            </table>
            <div style="padding:18px 20px;border-top:1px dashed #e5e7eb;color:#6b7280;font-size:12px;">
              이 메일은 저장 시점의 코스 상세 정보를 기반으로 생성되었습니다.
            </div>
          </div>
        </div>
        """

        text = (
            f"MJE DATE COURSE E-TICKET\n"
            f"title: {course_detail.course_title}\n"
            f"course_id: {course_detail.course_id}\n"
            f"condition: {condition_text}\n\n"
            + "\n".join(rows_text)
        )

        return html, text

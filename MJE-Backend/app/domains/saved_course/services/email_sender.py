from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import settings


@dataclass(frozen=True)
class EmailSendResult:
    success: bool
    error_message: str | None = None


class EmailSender:
    def send(self, to_email: str, subject: str, html_body: str, text_body: str) -> EmailSendResult:
        if settings.mail_mode == "mock":
            return EmailSendResult(success=True)

        if not settings.smtp_host:
            return EmailSendResult(success=False, error_message="SMTP host is not configured.")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.mail_from
        message["To"] = to_email
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        try:
            if settings.smtp_use_tls:
                server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
                try:
                    server.starttls()
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(message)
                finally:
                    server.quit()
            else:
                server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
                try:
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(message)
                finally:
                    server.quit()
        except Exception as exc:  # noqa: BLE001
            return EmailSendResult(success=False, error_message=str(exc))

        return EmailSendResult(success=True)


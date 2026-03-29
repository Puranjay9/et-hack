"""Email provider abstraction — SendGrid / SMTP."""

import os
from typing import Optional


class EmailProvider:
    """Abstraction layer for email sending via SendGrid or SMTP."""

    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "outreach@yourdomain.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Sponsor Outreach")
        self.tracking_base_url = os.getenv("TRACKING_BASE_URL", "http://localhost:8000")

    def inject_tracking(self, html_body: str, outreach_id: str) -> str:
        """Inject open tracking pixel and wrap links for click tracking."""
        # Open tracking pixel
        tracking_pixel = f'<img src="{self.tracking_base_url}/track/open/{outreach_id}" width="1" height="1" style="display:none;" />'

        # Wrap links for click tracking
        import re
        def wrap_link(match):
            url = match.group(1)
            tracked_url = f"{self.tracking_base_url}/track/click/{outreach_id}?url={url}"
            return f'href="{tracked_url}"'

        tracked_body = re.sub(r'href="(https?://[^"]+)"', wrap_link, html_body)
        tracked_body += tracking_pixel

        return tracked_body

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        outreach_id: Optional[str] = None,
    ) -> bool:
        """Send email via SendGrid."""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content

            # Inject tracking if outreach_id provided
            if outreach_id:
                html_body = self.inject_tracking(html_body, outreach_id)

            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_body),
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            return response.status_code in (200, 201, 202)

        except Exception as e:
            print(f"Email send failed: {e}")
            return False


# Singleton
email_provider = EmailProvider()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from vents.notifiers.base import BaseNotifier
from vents.notifiers.spec import NotificationSpec
from vents.providers.kinds import ProviderKind
from vents.settings import VENTS_CONFIG


class EmailNotifier(BaseNotifier):
    notification_key = ProviderKind.EMAIL
    name = "Email"
    description = "Send email notifications via SMTP."
    raise_empty_context = True
    check_config = True
    validate_keys = ["recipients", "from_email"]

    @classmethod
    def _validate_config(cls, config) -> List[Dict]:
        """Validate email configuration."""
        if not config:
            return []

        configs = config if isinstance(config, list) else [config]
        valid_configs = []

        for cfg in configs:
            if not cfg.get("smtp_host"):
                VENTS_CONFIG.logger.warning(
                    "Email config missing smtp_host: %s", cfg
                )
                continue

            if not cfg.get("recipients"):
                VENTS_CONFIG.logger.warning(
                    "Email config missing recipients: %s", cfg
                )
                continue

            valid_configs.append({
                "smtp_host": cfg["smtp_host"],
                "smtp_port": cfg.get("smtp_port", 587),
                "smtp_user": cfg.get("smtp_user"),
                "smtp_password": cfg.get("smtp_password"),
                "from_email": cfg.get("from_email", "noreply@polyaxon.com"),
                "recipients": cfg["recipients"],
                "use_tls": cfg.get("use_tls", True),
                "use_ssl": cfg.get("use_ssl", False),
            })

        return valid_configs

    @classmethod
    def serialize_notification_to_context(cls, notification: NotificationSpec) -> Dict:
        return {
            "subject": notification.title,
            "body_text": notification.details,
            "body_html": cls._build_html_body(notification),
        }

    @classmethod
    def _build_html_body(cls, notification: NotificationSpec) -> str:
        """Build HTML email body from notification."""
        color = notification.color or "#0076D7"
        url_section = ""
        if notification.url:
            url_section = f'<p><a href="{notification.url}">View Details</a></p>'

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 16px;">
                <h2 style="margin: 0 0 10px 0;">{notification.title}</h2>
                <p style="color: #666; margin: 0 0 10px 0;">{notification.description}</p>
                <div style="background: #f5f5f5; padding: 12px; border-radius: 4px;">
                    {notification.details}
                </div>
                {url_section}
            </div>
            <p style="color: #999; font-size: 12px; margin-top: 20px;">
                Sent by {VENTS_CONFIG.project_name}
            </p>
        </body>
        </html>
        """

    @classmethod
    def _prepare(cls, context: Dict) -> Dict:
        context = super()._prepare(context)
        return {
            "subject": context.get("subject", "Notification"),
            "body_text": context.get("body_text", ""),
            "body_html": context.get("body_html"),
        }

    @classmethod
    def _execute(cls, data: Dict, config: List[Dict]) -> Optional[Any]:
        for cfg in config:
            try:
                cls._send_email(
                    smtp_host=cfg["smtp_host"],
                    smtp_port=cfg["smtp_port"],
                    smtp_user=cfg.get("smtp_user"),
                    smtp_password=cfg.get("smtp_password"),
                    from_email=cfg["from_email"],
                    recipients=cfg["recipients"],
                    subject=data["subject"],
                    body_text=data["body_text"],
                    body_html=data.get("body_html"),
                    use_tls=cfg.get("use_tls", True),
                    use_ssl=cfg.get("use_ssl", False),
                )
            except Exception as e:
                VENTS_CONFIG.logger.warning(
                    "Could not send email notification: %s", e, exc_info=True
                )

    @classmethod
    def _send_email(
        cls,
        smtp_host: str,
        smtp_port: int,
        smtp_user: Optional[str],
        smtp_password: Optional[str],
        from_email: str,
        recipients: List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        use_tls: bool = True,
        use_ssl: bool = False,
    ) -> None:
        """Send email via SMTP."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = ", ".join(recipients)

        # Attach plain text
        msg.attach(MIMEText(body_text, "plain"))

        # Attach HTML if provided
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        # Connect and send
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)

        try:
            if use_tls and not use_ssl:
                server.starttls()

            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            server.sendmail(from_email, recipients, msg.as_string())
        finally:
            server.quit()
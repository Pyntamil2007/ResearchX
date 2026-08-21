import os
import smtplib
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from dotenv import dotenv_values
from app.core.config import settings
from app.database.database import SessionLocal
from app.models.notification import InAppNotification

# Configure logger for email diagnostics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("researchx.email")

class EmailService:
    @staticmethod
    def _get_live_smtp_credentials() -> dict:
        """
        Dynamically fetch SMTP configuration from backend/.env and settings.
        Ensures credentials updated in .env are picked up immediately.
        """
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        env_vals = dotenv_values(env_path) if env_path.exists() else {}

        smtp_email = (
            env_vals.get("SMTP_EMAIL") or
            os.getenv("SMTP_EMAIL") or
            settings.SMTP_EMAIL or
            ""
        ).strip()

        raw_password = (
            env_vals.get("SMTP_PASSWORD") or
            os.getenv("SMTP_PASSWORD") or
            settings.SMTP_PASSWORD or
            ""
        )
        # Clean Gmail App Password: remove all spaces (e.g. 'abcd efgh ijkl mnop' -> 'abcdefghijklmnop')
        smtp_password = raw_password.replace(" ", "").strip()

        smtp_server = (
            env_vals.get("SMTP_SERVER") or
            os.getenv("SMTP_SERVER") or
            settings.SMTP_SERVER or
            "smtp.gmail.com"
        ).strip()

        try:
            smtp_port = int(
                env_vals.get("SMTP_PORT") or
                os.getenv("SMTP_PORT") or
                settings.SMTP_PORT or
                587
            )
        except (ValueError, TypeError):
            smtp_port = 587

        from_name = (
            env_vals.get("SMTP_FROM_NAME") or
            os.getenv("SMTP_FROM_NAME") or
            settings.SMTP_FROM_NAME or
            "ResearchX Team"
        ).strip()

        return {
            "email": smtp_email,
            "password": smtp_password,
            "server": smtp_server,
            "port": smtp_port,
            "from_name": from_name
        }

    @classmethod
    def send_welcome_email(cls, user_email: str, user_name: str, user_id: int = None) -> dict:
        """
        Send a real welcome / account-creation email to the newly registered user via Gmail SMTP.
        Ensures passwords are NEVER sent in emails, credentials are never exposed, and creates in-app notification.
        """
        recipient_name = user_name or "Researcher"
        recipient_email = user_email.strip()
        subject = "Welcome to ResearchX – Account Created Successfully"

        # Exact specified plain text content
        text_content = f"""Hello {recipient_name},

Your ResearchX account has been created successfully.

Registered email: {recipient_email}

You can now log in to ResearchX and analyze research papers.

Thank you,
ResearchX Team"""

        # Professional Times New Roman styled HTML content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: "Times New Roman", Times, serif; background-color: #0a0e17; color: #f1f5f9; padding: 20px; }}
  .container {{ max-width: 600px; margin: 0 auto; background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 32px; }}
  .brand {{ color: #6366f1; font-size: 24px; font-weight: bold; margin-bottom: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 16px; }}
  p {{ font-size: 16px; line-height: 1.7; color: #e2e8f0; margin-bottom: 16px; }}
  .info-box {{ background: rgba(99, 102, 241, 0.1); border-left: 4px solid #6366f1; padding: 14px 18px; border-radius: 6px; margin: 20px 0; }}
  .button {{ display: inline-block; background: #6366f1; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; margin-top: 12px; }}
  .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #1e293b; color: #94a3b8; font-size: 14px; }}
</style>
</head>
<body>
  <div class="container">
    <div class="brand">ResearchX – Web Research Analyzer</div>
    <p>Hello {recipient_name},</p>
    <p>Your ResearchX account has been created successfully.</p>
    <div class="info-box">
      <strong>Registered email:</strong> {recipient_email}
    </div>
    <p>You can now log in to ResearchX and analyze research papers.</p>
    <p><a href="http://127.0.0.1:5173/login" class="button">Log In to ResearchX</a></p>
    <div class="footer">
      <p>Thank you,<br><strong>ResearchX Team</strong></p>
    </div>
  </div>
</body>
</html>"""

        # Step 1: Create in-app notification in SQLite
        if user_id:
            try:
                db = SessionLocal()
                notif = InAppNotification(
                    user_id=user_id,
                    title="Welcome to ResearchX!",
                    message=f"Your ResearchX account has been created. A confirmation email has been dispatched to {recipient_email}.",
                    notification_type="welcome",
                    is_read=False
                )
                db.add(notif)
                db.commit()
                db.close()
            except Exception as e:
                logger.warning(f"[NOTIFICATION WARNING] Could not record in-app notification: {e}")

        # Step 2: Retrieve live SMTP credentials
        creds = cls._get_live_smtp_credentials()

        if not creds["email"] or not creds["password"]:
            error_msg = "SMTP_EMAIL or SMTP_PASSWORD (Gmail App Password) not configured in backend/.env."
            logger.warning(f"[SMTP UNCONFIGURED] {error_msg} Account created successfully, email skipped for {recipient_email}.")
            return {
                "sent": False,
                "status": "unconfigured",
                "message": "Account created, but the confirmation email could not be sent (SMTP not configured in backend/.env).",
                "recipient": recipient_email
            }

        # Step 3: Connect and send via Gmail SMTP
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = formataddr((str(Header(creds["from_name"], "utf-8")), creds["email"]))
            msg["To"] = formataddr((str(Header(recipient_name, "utf-8")), recipient_email))

            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            logger.info(f"[SMTP CONNECTING] Connecting to {creds['server']}:{creds['port']} via STARTTLS for {recipient_email}...")
            
            server = smtplib.SMTP(creds["server"], creds["port"], timeout=12.0)
            server.ehlo()
            if creds["port"] == 587:
                server.starttls()
                server.ehlo()

            logger.info(f"[SMTP AUTHENTICATING] Authenticating with Gmail account: {creds['email']}...")
            server.login(creds["email"], creds["password"])

            logger.info(f"[SMTP SENDING] Dispatching message to recipient: {recipient_email}...")
            send_errs = server.sendmail(creds["email"], [recipient_email], msg.as_string())
            server.quit()

            if send_errs:
                logger.error(f"[SMTP RECIPIENT FAILURE] Refused recipients: {send_errs}")
                return {
                    "sent": False,
                    "status": "recipient_refused",
                    "message": "Account created, but the confirmation email could not be sent (recipient address was rejected by mail server).",
                    "recipient": recipient_email
                }

            logger.info(f"[SMTP SUCCESS] 250 OK: Welcome email delivered successfully to {recipient_email}.")
            return {
                "sent": True,
                "status": "delivered",
                "message": "Account created successfully. A confirmation email has been sent to your registered address.",
                "recipient": recipient_email
            }

        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(
                f"[SMTP AUTHENTICATION FAILURE] Gmail authentication rejected (Code {auth_err.smtp_code}): {auth_err.smtp_error.decode('utf-8', errors='ignore') if isinstance(auth_err.smtp_error, bytes) else auth_err.smtp_error}. "
                "Ensure you generated a 16-character App Password at https://myaccount.google.com/apppasswords with 2-Step Verification enabled."
            )
            return {
                "sent": False,
                "status": "auth_failed",
                "message": "Account created, but the confirmation email could not be sent (Gmail SMTP authentication failed).",
                "recipient": recipient_email
            }
        except smtplib.SMTPConnectError as conn_err:
            logger.error(f"[SMTP CONNECTION FAILURE] Could not connect to {creds['server']}:{creds['port']}: {conn_err}")
            return {
                "sent": False,
                "status": "connection_failed",
                "message": "Account created, but the confirmation email could not be sent (SMTP connection failure).",
                "recipient": recipient_email
            }
        except smtplib.SMTPRecipientsRefused as recip_err:
            logger.error(f"[SMTP INVALID RECIPIENT] Recipient email address refused by Gmail: {recipient_email} - {recip_err}")
            return {
                "sent": False,
                "status": "invalid_recipient",
                "message": "Account created, but the confirmation email could not be sent (invalid recipient address).",
                "recipient": recipient_email
            }
        except Exception as e:
            logger.error(f"[SMTP SENDING FAILURE] Unexpected error sending email to {recipient_email}: {str(e)}")
            return {
                "sent": False,
                "status": "failed",
                "message": "Account created, but the confirmation email could not be sent.",
                "recipient": recipient_email
            }

    @classmethod
    def test_smtp_connection(cls, test_recipient: str) -> dict:
        """
        Diagnostic function to test SMTP configuration independently from user registration.
        """
        creds = cls._get_live_smtp_credentials()

        if not creds["email"] or not creds["password"]:
            return {
                "success": False,
                "stage": "configuration",
                "message": "SMTP_EMAIL or Gmail App Password is not set in backend/.env.",
                "configured": False,
                "server": creds["server"],
                "port": creds["port"]
            }

        try:
            subject = "ResearchX – SMTP Configuration Test"
            text_body = f"This is an automated test email confirming that Gmail SMTP is properly configured for ResearchX.\n\nSender: {creds['email']}\nRecipient: {test_recipient}\nServer: {creds['server']}:{creds['port']}"

            msg = MIMEMultipart("alternative")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = formataddr((str(Header(creds["from_name"], "utf-8")), creds["email"]))
            msg["To"] = test_recipient.strip()
            msg.attach(MIMEText(text_body, "plain", "utf-8"))

            server = smtplib.SMTP(creds["server"], creds["port"], timeout=12.0)
            server.ehlo()
            if creds["port"] == 587:
                server.starttls()
                server.ehlo()

            server.login(creds["email"], creds["password"])
            server.sendmail(creds["email"], [test_recipient.strip()], msg.as_string())
            server.quit()

            return {
                "success": True,
                "stage": "completed",
                "message": f"Test email sent successfully to {test_recipient.strip()} via {creds['server']}:{creds['port']}.",
                "recipient": test_recipient.strip(),
                "server": creds["server"],
                "port": creds["port"]
            }
        except smtplib.SMTPAuthenticationError as e:
            return {
                "success": False,
                "stage": "authentication",
                "message": "Gmail authentication failed (535). Please ensure 2-Step Verification is enabled and use a 16-character App Password from https://myaccount.google.com/apppasswords.",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "stage": "connection_or_delivery",
                "message": f"SMTP test failed: {str(e)}",
                "details": str(e)
            }

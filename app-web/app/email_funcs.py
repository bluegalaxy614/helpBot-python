import logging
import smtplib
import ssl

from email.message import EmailMessage

from app import settings

logger = logging.getLogger(__name__)


def smtp_ssl_connection():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    connection = smtplib.SMTP('smtp.sendgrid.net', 587)
    connection.ehlo()
    connection.starttls(context=context)
    connection.ehlo()
    connection.login(settings.SENDGRID_USERNAME, settings.SENDGRID_API_KEY)
    return connection


def send_reset_password_email(from_email, to_email, reset_link):

    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request"
    msg["From"] = settings.APP_EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(f"Hello, here is the link to reset your password: {reset_link}")

    try:
        connection = smtp_ssl_connection()
        connection.send_message(msg)
        connection.close()
    except Exception as error:
        return False, "Unable to send email!"
    return True, "Check your inbox"


def send_verify_email_email(from_email, to_email, link):
    msg = EmailMessage()
    msg["Subject"] = "HelpBot Email Verification."
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(f"Hello, Finish the registration process with this link: {link}")

    try:
        connection = smtp_ssl_connection()
        connection.send_message(msg)
        connection.close()
    except Exception as error:
        logger.error("Failed to send email")
        logger.error(str(error))
        return False, "Unable to send email!"
    return True, "Check your inbox"



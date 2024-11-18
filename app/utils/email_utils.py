import os
from pydantic import EmailStr
import smtplib
from email.mime.text import MIMEText
from global_config import SMTP_HOST, SMTP_PORT


EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']


def send_email(target_email: EmailStr | list[EmailStr], subject: str, content: str) -> bool:
    if not isinstance(target_email, list):
        target_email = [target_email]

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = target_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, target_email, msg.as_string())
        return True


def send_activation_email(target_email: EmailStr, activation_link: str):
    return send_email(
        target_email,
        'Activate your account',
        f'Click the link to activate your account: {activation_link}'
    )

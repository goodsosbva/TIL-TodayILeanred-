import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import get_settings


class EmailService:
    def send_welcome_email(self, receiver_email: str):
        settings = get_settings()

        message = MIMEMultipart()
        message["From"] = settings.email_sender
        message["To"] = receiver_email
        message["Subject"] = "회원가입을 환영합니다."

        body = "TIL 서비스를 이용해주셔서 감사합니다."
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(settings.email_host, settings.email_port) as server:
            server.login(settings.email_sender, settings.email_password)
            server.send_message(message)

from user.application.email_service import EmailService

try:
    from celery import Task
except ImportError as e:
    raise RuntimeError("Celery is required. Install celery[redis].") from e


class SendWelcomeEmailTask(Task):
    name = "send_welcome_email_task"

    def run(self, receiver_email: str):
        EmailService().send_welcome_email(receiver_email)

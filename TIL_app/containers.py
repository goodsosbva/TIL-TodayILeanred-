from dependency_injector import containers, providers

from common.messaging import send_welcome_email_task
from note.application.note_service import NoteService
from note.infra.repository.note_repo import NoteRepository
from user.application.email_service import EmailService
from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "note",
            "user",
        ],
    )

    note_repo = providers.Factory(NoteRepository)
    note_service = providers.Factory(NoteService, note_repo=note_repo)
    email_service = providers.Factory(EmailService)
    send_welcome_email_task = providers.Object(send_welcome_email_task)
    user_repo = providers.Factory(UserRepository)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        send_welcome_email_task=send_welcome_email_task,
    )

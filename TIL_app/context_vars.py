from contextvars import ContextVar

from common.auth import CurrentUser


user_context: ContextVar[CurrentUser | None] = ContextVar(
    "current_user",
    default=None,
)

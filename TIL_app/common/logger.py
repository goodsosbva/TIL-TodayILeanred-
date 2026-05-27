import logging

from context_vars import user_context

LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s:\tuser: %(user)s: %(message)s"


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "user"):
            record.user = "Anonymous"
        return super().format(record)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        user = user_context.get()
        record.user = str(user) if user else "Anonymous"
        return True


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter(LOG_FORMAT))

logger = logging.getLogger("til-app")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    logger.addHandler(handler)

if not any(isinstance(filter_, ContextFilter) for filter_ in logger.filters):
    logger.addFilter(ContextFilter())

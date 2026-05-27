from time import perf_counter

from fastapi import FastAPI, Request

from common.auth import CurrentUser, Role, decode_access_token
from common.logger import logger
from context_vars import user_context


def create_middlewares(app: FastAPI):
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        token = user_context.set(None)
        current_user = _get_user_from_authorization(
            request.headers.get("Authorization")
        )
        if current_user:
            user_context.set(current_user)

        started_at = perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.info(
                "%s %s -> %s %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
            return response
        except Exception:
            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.exception(
                "%s %s -> error %.2fms",
                request.method,
                request.url.path,
                elapsed_ms,
            )
            raise
        finally:
            user_context.reset(token)


def _get_user_from_authorization(authorization: str | None) -> CurrentUser | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme != "Bearer" or not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")
        if not user_id or not role:
            return None

        return CurrentUser(id=user_id, role=Role(role))
    except Exception:
        return None

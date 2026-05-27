import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from config import get_settings
from containers import Container
from middlewares import create_middlewares

from note.interface.controllers import note_controller
from user.interface.controllers import user_controller

app = FastAPI()
container = Container()
container.wire(modules=[note_controller, user_controller])
app.container = container

app.include_router(note_controller.router)
app.include_router(user_controller.router)

create_middlewares(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )


@app.get("/")
def hello():
    return {"Hello": "FastAPI"}


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
from fastapi import  BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager
from app.core.exceptions import FastShipError, InvalidToken
from app.database.session import create_db_tables

from app.api.router import master_router
from app.services.notification import NotificationService

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    await create_db_tables()
    yield

app = FastAPI(lifespan = lifespan_handler)

app.include_router(master_router)


def error_handler(request,exception:FastShipError):
    return JSONResponse(
        content = {"detail":exception.detail},
        status_code = exception.status_code,
    )

app.add_exception_handler(FastShipError,error_handler)



@app.get("/mail")
async def send_test_mail(tasks:BackgroundTasks):
    tasks.add_task(
        NotificationService().send_email,
        recipients=["akira.ise.m@gmail.com"],
        subject = "Test Mail Coming Through Once",
        body = "You should not be interesteted in every body"
    )

    return {"detail":"Sending mail..."}


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )



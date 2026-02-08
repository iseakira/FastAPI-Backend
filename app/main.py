from fastapi import  FastAPI
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager
from app.database.session import create_db_tables

from app.api.router import router

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    create_db_tables()
    yield

app = FastAPI(lifespan = lifespan_handler)

app.include_router(router)


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )



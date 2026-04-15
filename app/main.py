from fastapi import  FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager
from app.core.exceptions import FastShipError
from app.database.session import create_db_tables

from app.api.router import master_router

@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    await create_db_tables()
    yield

description = """
Delivery Management System for sellers and delivery agents

### Seller
- Submit shipment effortlessly
- Share tracking links with coustomers

### Delivery Agent
- Auto accept shipments
- Track and update shipment status
- Email and SMS notifications


"""

app = FastAPI(
    lifespan = lifespan_handler,
    title="FastShip",
    description=description
    )

app.include_router(master_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)


def error_handler(request,exception:FastShipError):
    return JSONResponse(
        content = {"detail":exception.detail},
        status_code = exception.status_code,
    )

app.add_exception_handler(FastShipError,error_handler)


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )



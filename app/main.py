from datetime import datetime, timedelta
from fastapi import  FastAPI,status
from fastapi.exceptions import HTTPException as HttpException
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from app.database.models import Shipment, ShipmentStatus

from .schemas import ShipmentRead, ShipmentCreate, ShipmentUpdate
from app.database.session import create_db_tables, SessionDep



@asynccontextmanager
async def lifespan_handler(app:FastAPI):
    create_db_tables()
    yield


app = FastAPI(lifespan = lifespan_handler)


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )

@app.get("/shipment", response_model=ShipmentRead)
async def get_shipment(id:int,session:SessionDep):
    shipment = await session.get(Shipment,id)
    if shipment is None:
        raise HttpException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Shipment not found"
        )
    return shipment

@app.post("/shipment",response_model=None)
def create_shipment(shipment:ShipmentCreate,session:SessionDep):
    new_shipment = Shipment(
        **shipment.model_dump(),
        status = ShipmentStatus.placed,
        estimated_delivery = datetime.now() + timedelta(days=3)
    )
    session.add(new_shipment)
    session.commit()
    session.refresh(new_shipment)
    return {"id": new_shipment.id}


@app.patch("/shipment",response_model=ShipmentRead)
def patch_shipment(id:int, shipment_update:ShipmentUpdate, session:SessionDep):
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HttpException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    shipment=session.get(Shipment,id)
    shipment.sqlmodel_update(update)
    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment

@app.delete("/shipment")
def delete_shipment(id:int,session:SessionDep):
    session.delete(
        session.get(Shipment,id)
    )
    session.commit()
    return {"detail":"Shipment deleted"}


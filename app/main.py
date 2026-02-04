from fastapi import FastAPI,status
from fastapi.exceptions import HTTPException as HttpException
from scalar_fastapi import get_scalar_api_reference
from .schemas import ShipmentRead, ShipmentCreate, ShipmentUpdate
from .database import Database





app = FastAPI()

db = Database()


@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )

@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id:int) :
    shipment = db.get(id)
    if shipment is None:
        raise HttpException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Shipment not found"
        )
    return shipment

@app.post("/shipment")
def create_shipment(shipment:ShipmentCreate):
    new_id = db.create(shipment)

    return {"id": new_id}


@app.patch("/shipment",response_model=ShipmentRead)
def patch_shipment(id:int, shipment:ShipmentUpdate):
    shipment=db.update(id,shipment)
    return shipment

@app.delete("/shipment")
def delete_shipment(id:int):
    db.delete(id)
    return {"message":f"Shipment {id} deleted successfully"}

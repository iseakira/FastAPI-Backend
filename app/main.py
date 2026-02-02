from fastapi import FastAPI,status
from fastapi.exceptions import HTTPException as HttpException
from scalar_fastapi import get_scalar_api_reference
from .schemas import ShipmentRead, ShipmentStatus, ShipmentCreate, ShipmentUpdate





app = FastAPI()

shipments = {
   12076: {
        "weight":2.0,
        "content":"Books",
        "status": "in transit",
        "destination": 101,
   },
    12077: {
          "weight":5.5,
          "content":"Electronics",
          "status": "delivered",
          "destination": 102,
    },
    12078: {
          "weight":1.2,
          "content":"Clothes",
          "status": "pending",
          "destination": 103,
    },
    12079: {
          "weight":3.0,
          "content":"Toys",
          "status": "in transit",
          "destination": 104,
    }
}

@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )

@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id:int) :
    if id not in shipments:
        raise HttpException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Shipment not found"
        )
    return shipments[id]

@app.get("/shipment/{field}")
def get_shipment_field(field:str, id:int):
    return {
        field: shipments[id][field]
    }

@app.post("/shipment")
def create_shipment(body:ShipmentCreate):
    new_id = max(shipments.keys()) + 1
    shipments[new_id] = {
        "weight": body.weight,
        "content": body.content,
        "destination": body.destination,
        "status": "placed"
   }
    return {"id": new_id}

@app.put("/shipment")
def update_shipment(id:int, content:str, weight:float, status:str):
    shipments[id] = {
        "weight":weight,
        "content":content,
        "status":status
    }
    return shipments[id]

@app.patch("/shipment",response_model=ShipmentRead)
def patch_shipment(id:int, body:ShipmentUpdate):
    shipments[id].update(body)
    return shipments[id]

@app.delete("/shipment")
def delete_shipment(id:int):
    shipments.pop(id)
    return {"detail":"Shipment with id {id} is deleted"}

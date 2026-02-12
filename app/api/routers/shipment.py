from fastapi import APIRouter, HTTPException, status
from app.api.schemas.shipment import ShipmentRead, ShipmentCreate, ShipmentUpdate
from app.api.dependencies import ServiceDep

router = APIRouter()

@router.get("/shipment", response_model=ShipmentRead)
async def get_shipment(id:int,service:ServiceDep):
    shipment = await service.get(id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Shipment not found"
        )
    return shipment

@router.post("/shipment",response_model=None)
async def create_shipment(shipment:ShipmentCreate,service:ServiceDep):
    return await service.add(shipment)


@router.patch("/shipment",response_model=ShipmentRead)
async def patch_shipment(id:int, shipment_update:ShipmentUpdate, service:ServiceDep):
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    shipment = await service.update(id,shipment_update)
    return shipment

@router.delete("/shipment")
async def delete_shipment(id:int,service:ServiceDep):

    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted"}




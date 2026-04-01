from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from app.api.schemas.shipment import ShipmentRead, ShipmentCreate, ShipmentUpdate
from app.api.dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep

router = APIRouter()

@router.get("/shipment", response_model=ShipmentRead)
async def get_shipment(id:UUID,service:ShipmentServiceDep):
    shipment = await service.get(id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Shipment not found"
        )
    return shipment

@router.get('/track')
async def get_tracking(id:UUID,service:ShipmentServiceDep):
    shipment = await service.get(id)
    return HTMLResponse(
        content = f"<body><h1>Order #{shipment.id}:{shipment.status}</h1></body>"
    )


@router.post("/shipment",response_model=None)
async def create_shipment(
    shipment:ShipmentCreate,
    service:ShipmentServiceDep,
    seller:SellerDep
):
    return await service.add(shipment,seller)


@router.patch("/shipment",response_model=ShipmentRead)
async def update_shipment(
    id:UUID, shipment_update:ShipmentUpdate,
    partner:DeliveryPartnerDep,
    service:ShipmentServiceDep):

    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    return await service.update(
        id,shipment_update,partner
    )

@router.get("/cancel", response_model = ShipmentRead)
async def cancel_shipment(
    id:UUID,
    seller:SellerDep,
    service:ShipmentServiceDep
):
    await service.cancel(id,seller)

@router.delete("/shipment")
async def delete_shipment(id:UUID,service:ShipmentServiceDep):

    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted"}




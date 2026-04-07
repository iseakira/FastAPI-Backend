from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.schemas.shipment import ShipmentRead, ShipmentCreate, ShipmentReview, ShipmentUpdate
from app.api.dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep
from app.utils import TEMPLATE_DIR

from app.config import app_settings

router = APIRouter(prefix="/shipment" ,tags=["Shipment"])

templates=Jinja2Templates(TEMPLATE_DIR)

@router.get("/", response_model=ShipmentRead)
async def get_shipment(id:UUID,service:ShipmentServiceDep):
    shipment = await service.get(id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Shipment not found"
        )
    return shipment

@router.get('/track')
async def get_tracking(request:Request, id:UUID,service:ShipmentServiceDep):
    shipment = await service.get(id)
    context = shipment.model_dump()
    context["status"] = shipment.status
    context["partner"] = shipment.delivery_partner.name
    context["timeline"]=shipment.timeline

    return templates.TemplateResponse(
        request,
        name="track.html",
        context=context
    )


@router.post("/",response_model=None)
async def create_shipment(
    shipment:ShipmentCreate,
    service:ShipmentServiceDep,
    seller:SellerDep
):
    return await service.add(shipment,seller)


@router.patch("/",response_model=ShipmentRead)
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

@router.delete("/")
async def delete_shipment(id:UUID,service:ShipmentServiceDep):

    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted"}



@router.get("/review")
async def submit_review(
    request:Request,
    token:str,
    ):
    templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "review_url":f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"
        }

    )



### Submit a review shipment
@router.post("/review")
async def submit_review(
    token:str,
    rating:Annotated[int,Form(ge=1,le=5)],
    comment:Annotated[str | None, Form()],
    service:ShipmentServiceDep,
    ):
    await service.rate(token,rating,comment)
    return {"detail:Review sbmitted"}


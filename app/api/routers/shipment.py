from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.schemas.shipment import ShipmentRead, ShipmentCreate, ShipmentReview, ShipmentUpdate
from app.api.dependencies import DeliveryPartnerDep, SellerDep, SessionDep, ShipmentServiceDep
from app.core.exceptions import NothingToUpdate
from app.database.models import TagName
from app.utils import TEMPLATE_DIR

from app.config import app_settings

router = APIRouter(prefix="/shipment" ,tags=["Shipment"])

templates=Jinja2Templates(TEMPLATE_DIR)

@router.get("/", response_model=ShipmentRead)
async def get_shipment(id:UUID,service:ShipmentServiceDep):
    shipment = await service.get(id)
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
        raise NothingToUpdate()

    return await service.update(
        id,shipment_update,partner
    )

## Add a tag to a Shipment
@router.get("/tag",response_model=ShipmentRead)
async def add_tag_to_shipment(
    id:UUID,
    tag_name:TagName,
    service: ShipmentServiceDep,

):
    return await service.add_tag(id,tag_name)


## Remove a tag from a Shipment
@router.delete("/tag",response_model=ShipmentRead)
async def remove_tag_from_shipment(
    id:UUID,
    tag_name:TagName,
    service: ShipmentServiceDep,
):
    return await service.remove_tag(id,tag_name)

@router.get("/cancel", response_model = ShipmentRead)
async def cancel_shipment(
    id:UUID,
    seller:SellerDep,
    service:ShipmentServiceDep
):
    return await service.cancel(id,seller)

@router.get("/tagged",response_model=list[ShipmentRead])
async def get_shipments_with_tag(
    tag_name:TagName,
    session:SessionDep,
    ):
    tag = await tag_name.tag(session)
    return tag.shipments


@router.delete("/")
async def delete_shipment(id:UUID,service:ShipmentServiceDep):

    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted"}



@router.get("/review")
async def submit_review(
    request:Request,
    token:str,
    ):
    return templates.TemplateResponse(
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
    return {"detail": "Review submitted"}


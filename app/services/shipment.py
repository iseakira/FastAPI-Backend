from uuid import UUID

from fastapi import HTTPException,status

from app.api.schemas.shipment import ShipmentCreate, ShipmentReview, ShipmentUpdate
from app.core.exceptions import ClientNotAuthorized, EntityNotFoundError
from app.database.models import DeliveryPartner, Review, Seller, ShipmentStatus, TagName
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Shipment
from datetime import datetime, timedelta

from app.database.redis import get_shipments_verification_code
from app.services.base import BaseService
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_url_safe_token

class ShipmentService(BaseService):
  def __init__(
      self,
      session:AsyncSession,
      partner_service:DeliveryPartnerService,
      event_service:ShipmentEventService):
    super().__init__(Shipment,session)
    self.partner_service = partner_service
    self.event_service = event_service


  async def get(self,id:UUID) -> Shipment:
    shipment = await self._get(id)
    if shipment is None:
      raise EntityNotFoundError()
    return shipment



  async def add(self,shipment_create:ShipmentCreate,seller:Seller) -> Shipment:
     new_shipment = Shipment(
        **shipment_create.model_dump(),
        status = ShipmentStatus.placed,
        estimated_delivery = datetime.now() + timedelta(days=3),
        seller_id=seller.id
    )
     partner =await self.partner_service.assign_shipment(
       new_shipment
       )
     new_shipment.delivery_partner_id= partner.id
     shipment =await self._add(new_shipment)
     await self.event_service.add(
       shipment=shipment,
       location = seller.zip_code,
       status = ShipmentStatus.placed,
       description = f"assigned to {partner.name}"
     )

     return shipment

## Update fields of a shipment
  async def update(self,id:UUID,shipment_update:ShipmentUpdate,partner:DeliveryPartner):
    shipment = await self.get(id)

    if shipment.delivery_partner_id != partner.id:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )

    if shipment_update.status == ShipmentStatus.delivered:
      code=get_shipments_verification_code(shipment.id)

      if code != shipment_update.verification_code:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Client not authorized"
        )



    update = shipment_update.model_dump(
      exclude_none=True,
      exclude=["verification_code"],
      )
    if shipment_update.estimated_delivery:
      shipment.estimated_delivery = shipment_update.estimated_delivery
    if len(update) > 0 or not shipment_update.estimated_delivery:
      await self.event_service.add(
      shipment=shipment,
      **update
    )


    return await self._update(shipment)

  async def cancel(self,id:UUID,seller:Seller) -> Shipment:
    shipment = await self.get(id)
    if shipment.seller_id != seller.id:
      raise ClientNotAuthorized()
    await self.event_service.add(
      shipment=shipment,
      status=ShipmentStatus.cancelled
    )
    return shipment

  async def delete(self,id:UUID)-> None:
    await self._delete(await self.get(id))


  async def add_tag(self,id:UUID, tag_name:TagName):
    shipment= await self.get(id)
    shipment.tags.append(await tag_name.tag(self.session))

    return await self._update(shipment)

  async def remove_tag(self,id:UUID, tag_name:TagName):
    shipment= await self.get(id)
    try:
      shipment.tags.remove(await tag_name.tag(self.session))

    except ValueError:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Tag doesn`t exist on shipment",
      )

    return await self._update(shipment)


  async def rate(self,token:str,rating:int, comment:str):
    token_data=decode_url_safe_token(token)

    if not token_data:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized",
      )

    shipment=self.get(UUID(token_data["id"]))
    new_review=Review(
      rating=rating,
      comment=comment if comment else None,
      shipment_id=shipment.id,
    )
    self.session.add(new_review)
    await self.session.commit()





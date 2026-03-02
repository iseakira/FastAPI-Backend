from fastapi import HTTPException,status
from sqlalchemy import Sequence, select,any_

from app.api.schemas.delivery_partner import DeliveryPartnerCreate

from .user import UserService
from app.database.models import DeliveryPartner, Shipment

class DeliveryPartnerService(UserService):
  def __init__(self,session):
    super().__init__(DeliveryPartner,session)

  async def add(self,delivery_partner:DeliveryPartnerCreate):
    return await self._add_user(
      delivery_partner
    )
  async def get_partner_by_zipcode(self,zipcode:int)->Sequence[DeliveryPartner]:
    result=await self.session.scalars(
      select(DeliveryPartner).where(
        zipcode == any_(DeliveryPartner.serviceable_zip_codes)
      )
    )
    return result.all()

  async def assign_shipment(self,shipment:Shipment):
    eligible_partner = await self.get_partner_by_zipcode(shipment.destination)

    for partner in eligible_partner:
      if partner.current_handling_capacity> 0:
        partner.shipments.append(shipment)
        return partner

    raise HTTPException(
      status_code = status.HTTP_406_NOT_ACCEPTABLE,
      detail = "No Delivery Partner Avaiable"
    )



  async def token(self,email,password):
    return await self._generate_token(email,password)

  async def update(self,partner:DeliveryPartner):
    return await self._update(partner)
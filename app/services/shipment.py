from uuid import UUID

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.database.models import Seller, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Shipment
from datetime import datetime, timedelta

from app.services.base import BaseService

class ShipmentService(BaseService):
  def __init__(self,session:AsyncSession):
    super().__init__(Shipment,session)


  async def get(self,id:UUID) -> Shipment:
    return await self._get(id)



  async def add(self,shipment_create:ShipmentCreate,seller:Seller) -> Shipment:
     new_shipment = Shipment(
        **shipment_create.model_dump(),
        status = ShipmentStatus.placed,
        estimated_delivery = datetime.now() + timedelta(days=3),
        seller_id=seller.id
    )
     return await self._add(new_shipment)

  async def update(self,id:int,shipment_update:ShipmentUpdate):
    shipment = await self.session.get(Shipment,id)
    shipment.sqlmodel_update(
        shipment_update.model_dump(exclude_none=True)
    )
    return await self._update(shipment)


  async def delete(self,id:UUID)-> None:
    await self._delete(self.get(id))



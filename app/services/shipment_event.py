
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService


class ShipmentEventService(BaseService):
  def __init__(self,session):
    super().__init__(ShipmentEvent,session)
    self.notification_service=NotificationService()

  async def add(
      self,
      shipment:Shipment,
      location:int=None,
      status:ShipmentStatus=None,
      description:str = None,
  ) -> ShipmentEvent:

    if not location or not status:
      last_event=await self.get_latest_event(shipment)
      location= location if location else last_event.location
      status = status if status else last_event.status

    new_event = ShipmentEvent(
      location=location,
      status=status,
      description=description if description else self._generate_description,
      shipment_id = shipment.id,
    )
    await self._notyfy(shipment,status)
    return await self._add(new_event)

  async def get_latest_event(self,shipment:Shipment):
    timeline=shipment.timeline
    timeline.sort(key=lambda item:item.created_at)[-1]
    return timeline[-1]

  def _generate_description(self,status:ShipmentStatus,location:int):
    match status:
      case ShipmentStatus.placed:
        return "assingned delivery partner"
      case ShipmentStatus.out_for_delivery:
        return "shipment out for delivery"
      case ShipmentStatus.delivered:
        return "successfilly delivered"
      case ShipmentStatus.cancelled:
        return "cancelled by seller"
      case _:
        return f"shipment at {location}"

  async def _notyfy(self,shipment:Shipment,status:ShipmentStatus):
    match status:
      case ShipmentStatus.placed:
        self.notification_service.send_mail(
          recipients=[shipment.client_contact_email],
          subject="Your Order is Shipped",
          body=f"Your order with {shipment.seller.name} is picked up delivery {shipment.delivery_partner}",

        )
      case ShipmentStatus.out_for_delivery:
       self.notification_service.send_mail(
          recipients=[shipment.client_contact_email],
          subject="Your Order is arriving",
          body="Our delivery executive is on their way"
                "to delivery your order. Please ensure you are available"
                 "to recieve the same" ,

        )


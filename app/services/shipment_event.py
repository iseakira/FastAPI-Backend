
from random import randint

from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.database.redis import add_shipments_vertification_code
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.config import app_settings
from app.utils import generate_url_safe_token


class ShipmentEventService(BaseService):
  def __init__(self,session,tasks):
    super().__init__(ShipmentEvent,session)
    self.notification_service=NotificationService(tasks)

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
    await self._notify(shipment,status)
    return await self._add(new_event)

  async def get_latest_event(self,shipment:Shipment):
    await self.session.refresh(shipment, attribute_names=["timeline"])
    timeline=shipment.timeline
    timeline.sort(key=lambda item:item.created_at)
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

  async def _notify(self,shipment:Shipment,status:ShipmentStatus):
    await self.session.refresh(shipment, attribute_names=["seller", "delivery_partner"])

    if status == ShipmentStatus.in_transit:
      return

    ## email情報を初期化
    subject:str
    context = {}
    template_name:str

    ## 各ケースに応じてメールの内容を変更
    match status:
      case ShipmentStatus.placed:
       subject = "Your Order is Placed",
       context["id"] = shipment.id
       context["seller"] = shipment.seller.name
       context["partner"] = shipment.delivery_partner.name
       template_name = "mail_placed.html"

      case ShipmentStatus.out_for_delivery:
        subject = "Your Order is Arriving Soon"
        template_name = "mail_out_for_delivery.html"

        code=randint(100_000,999_999)
        add_shipments_vertification_code(shipment.id,code)

        if shipment.client_contact_phone:
          await self.notification_service.send_sms(
            to=shipment.client_contact_phone,
            body="Your order is arriving soon share code with your delivery excutive "
          )
        else:
          context["vertification_code"] =code

      case ShipmentStatus.delivered:
        subject = "Your Order is Delivered"
        token=generate_url_safe_token({"id":str(shipment.id)})
        context["seller"] = shipment.seller.name
        context["review_url"] = f"https://{app_settings.APP_DOMAIN}/shipment/review/?token={token}"
        template_name = "mail_delivered.html"

      case ShipmentStatus.cancelled:
        subject = "Your Order is Cancelled ✖"
        template_name = "mail_cancelled.html"


    ## メール送信のための関数を呼び出す
    self.notification_service.send_email_with_template(

      recipients=[shipment.client_contact_email],
      subject=subject,
      context=context,
      template_name=template_name

    )
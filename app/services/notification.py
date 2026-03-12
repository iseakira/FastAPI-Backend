from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import notification_settings

class NotificationService:
  def __init__(self):
    self.fastmail=FastMail(
      ConnectionConfig(
        **notification_settings.model_dump()
  )
)
  async def send_mail(
      self,
      recipients:list[EmailStr],
      subject:str,
      body:str,
    ):
    await self.fastmail.send_message(
      message=MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.plain
      )
    )
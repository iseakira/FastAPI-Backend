from asgiref.sync import async_to_sync
from celery import Celery
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.config import db_settings,notification_settings
from app.utils import TEMPLATE_DIR

fast_mail=FastMail(
      ConnectionConfig(
        **notification_settings.model_dump(
          exclude=["TWILIO_SID","TWILIO_AUTH_TOKEN","TWILIO_NUMBER"]
        ),
        TEMPLATE_FOLDER=TEMPLATE_DIR
  )
)

send_message=async_to_sync(fast_mail.send_message)

app=Celery(
  "api_tasks",
  broker = db_settings.REDIS_URL(9)
)

@app.task
def send_mail(
  recipients:list[str],
  subject:str,
  body:str,
):
  send_message(MessageSchema(
    recipients,
    subject,
    body
  ))
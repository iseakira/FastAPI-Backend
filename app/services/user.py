from uuid import UUID

from fastapi import BackgroundTasks, HTTPException,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.config import app_settings

from app.database.models import User
from app.services.notification import NotificationService
from app.utils import decode_url_safe_token, generate_access_token, generate_url_safe_token

from .base import BaseService

ctx = CryptContext(schemes=["argon2"], deprecated="auto")

class UserService(BaseService):
  def __init__(self,model:User,session:AsyncSession,tasks:BackgroundTasks):
    self.model = model
    self.session=session
    self.notification_service = NotificationService(tasks)

  async def _add_user(self,data:dict,router_prefix:str):
    if not isinstance(data, dict):
       data = data.model_dump()

    user=self.model(
      **data,
      password_hash=ctx.hash(data["password"])

    )
    user = await self._add(user)
    token = generate_url_safe_token({
      "email":user.email,
      "id":str(user.id)
    })

    await self.notification_service.send_email_with_template(
      recipients = [user.email],
      subject="Verify Your Account With Fastship",
      context = {
        "username":user.name,
        "verification_url":f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}"
      },
      template_name="mail_email_verify.html",
    )

    return user

  async def verify_email(self,token:str):
    token_data=decode_url_safe_token(token)

    if not token_data:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token"
      )

    user=await self._get(UUID(token_data["id"]))
    user.email_verified = True

    await self._update(user)



  async def _get_by_email(self,email) -> User | None:
    return await self.session.scalar(
      select(self.model).where(self.model.email==email)
    )
  async def _generate_token(self,email,password)->str:
     user = await self._get_by_email(email)


     if user is None or  not ctx.verify(
       password,
       user.password_hash,
     ):
       raise HTTPException(
         status_code = status.HTTP_404_NOT_FOUND,
         detail = "Email or Password is not found"
       )

     if not user.email_verified:
        raise HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Email not verified",
       )

     token=generate_access_token(
       data={
         "user":{
           "name":user.name,
           "id":str(user.id),
         }
       }
     )

     return token
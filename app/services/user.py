from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.database.models import User
from app.utils import generate_access_token

from .base import BaseService

ctx = CryptContext(schemes=["argon2"], deprecated="auto")

class UserService(BaseService):
  def __init__(self,model:User,session:AsyncSession):
    self.model = model
    self.session=session

  async def _add_user(self,data:dict):
    user=self.model(
      **data,
      password_hash=ctx.hash(data["password"])

    )
    self._add(user)

  async def _get_by_email(self,email) -> User | None:
    return await self.session.scalar(
      select(self.model).where(self.model.email==email)
    )
  async def _generate_token(self,email,password)->str:
     user = self._get_by_email(email)


     if user is None or  not ctx.verify(
       password,
       user.password_hash,
     ):
       raise HTTPException(
         status_code = status.HTTP_404_NOT_FOUND,
         detail = "Email or Password is not found"
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
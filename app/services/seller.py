from datetime import datetime, timedelta
from fastapi import HTTPException,status
import jwt

from app.config import security_settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import  AsyncSession
from passlib.context import CryptContext
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

ctx = CryptContext(schemes=["argon2"], deprecated="auto")

class SellerService:
   def __init__(self,session:AsyncSession): # type: ignore
    self.session=session

   async def add(self, credentials:SellerCreate):
    seller = Seller(
        **credentials.model_dump(exclude=["password"]),
        password_hash=ctx.hash(credentials.password),
      )
    self.session.add(seller)
    await self.session.commit()
    await self.session.refresh(seller)

    return seller

   async def token(self,email,password) -> str:
     result=await self.session.execute(select(Seller).where(Seller.email == email))

     seller=result.scalar()

     if seller is None or  not ctx.verify(
       password,
       seller.password_hash,
     ):
       raise HTTPException(
         status_code = status.HTTP_404_NOT_FOUND,
         detail = "Email or Password is not found"
       )

     token=jwt.encode(
       payload={
         "user":{
           "name":seller.name,
           "email":seller.email,

         },
         "exp":datetime.now() + timedelta(days=1)
       },
       algorithm=security_settings.JWT_ALGORITHM,
       key=security_settings.JWT_SECRET,
     )
     jwt.decode(
       "token",

     )
     return token





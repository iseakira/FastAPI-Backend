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



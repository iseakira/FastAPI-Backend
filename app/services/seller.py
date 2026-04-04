
from sqlalchemy.ext.asyncio import  AsyncSession
from passlib.context import CryptContext
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from app.services.user import UserService


ctx = CryptContext(schemes=["argon2"], deprecated="auto")

class SellerService(UserService):
   def __init__(self,session:AsyncSession,tasks): # type: ignore
    super().__init__(Seller, session, tasks)

   async def add(self, seller_create:SellerCreate):
     return await self._add_user(
       seller_create.model_dump(),
       "seller"
       )

   async def token(self,email,password) -> str:
     return await self._generate_token(email,password)





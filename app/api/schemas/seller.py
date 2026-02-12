from pydantic import BaseModel, EmailStr


class SellerCreate(BaseModel):
  name:str
  email:EmailStr
  password:str
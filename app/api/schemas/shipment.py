from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.database.models import Seller, ShipmentEvent, ShipmentStatus, TagName

class BaseShipment(BaseModel):
    content:str = Field(max_length=30)
    weight:float = Field(le=25, ge=1)
    destination:int

class TagRead(BaseModel):
    name: TagName
    instruction:str

class ShipmentRead(BaseShipment):
    id:UUID
    timeline:list[ShipmentEvent]
    estimated_delivery:datetime
    tags:list[TagRead]

class ShipmentCreate(BaseShipment):
    client_contact_email:EmailStr
    client_contact_phone:int | None = Field(default = None)

class ShipmentUpdate(BaseModel):
    location : int | None = Field(default = None)
    status:ShipmentStatus | None = Field(default=None)
    verification_code:int | None = Field(default=None)
    description:str | None = Field(default=None)
    estimated_delivery:datetime | None = Field(default=None)

class ShipmentReview(BaseModel):
    rating:int = Field(ge=1,le=5)
    comment:str | None = Field(default=None)




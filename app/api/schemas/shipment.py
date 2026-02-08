from datetime import datetime
from pydantic import BaseModel, Field
from app.database.models import ShipmentStatus
from enum import Enum

class BaseShipment(BaseModel):
    content:str = Field(max_length=30)
    weight:float = Field(le=25, ge=1)
    destination:int

class ShipmentRead(BaseShipment):
    status:ShipmentStatus
    estimated_delivery:datetime

class ShipmentCreate(BaseShipment):
    pass

class ShipmentUpdate(BaseModel):
    status:ShipmentStatus | None = Field(default=None)
    estimated_delivery:datetime | None = Field(default=None)

class ShipmentStatus(str,Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"

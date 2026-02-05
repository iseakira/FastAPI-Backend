from sqlmodel import SQLModel,Field
from enum import Enum
from datetime import datetime

class ShipmentStatus(str,Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"

class Shipment(SQLModel):
  __tabalename__ = "shipment"

  id:int = Field(primary_key=True)
  content:str
  weight:float = Field(le=25)
  status:ShipmentStatus
  estimated_delivery:datetime

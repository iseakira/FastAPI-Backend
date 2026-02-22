from pydantic import EmailStr
from sqlmodel import Column, Relationship, SQLModel,Field
from uuid import uuid4,UUID
from datetime import datetime
from enum import Enum
from sqlalchemy.dialects import postgresql


class ShipmentStatus(str,Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
class Shipment(SQLModel, table=True):
  __tablename__ = "shipment"

  id:UUID = Field(
     sa_column=Column(
        ## UUIDの扱いはDBごとに違うので明示
        postgresql.UUID,
        ##UUIDの生成ルールを関数で与えてる
        default=uuid4,
        primary_key=True,
     )
  )
  content:str
  weight:float = Field(le=25)
  status:ShipmentStatus
  destination:int
  estimated_delivery:datetime

  seller_id:UUID = Field(foreign_key="seller.id")
  ## Sellerクラスのオブジェクトを引っ張てShipmentクラスとの繋がりを書きたいだけ、舌も同じ
  seller:"Seller"=Relationship(
     back_populates="shipments",
     sa_relationship_kwargs={"lazy":"selectin"})

class Seller(SQLModel, table=True):
   _tablename_="seller"

   id:UUID=Field(
     sa_column=Column(
        ## UUIDの扱いはDBごとに違うので明示
        postgresql.UUID,
        ##UUIDの生成ルールを関数で与えてる
        default=uuid4,
        primary_key=True,
     )
  )
   name:str
   email: EmailStr
   password_hash:str
   shipments:list[Shipment]=Relationship(
      back_populates="seller",
      sa_relationship_kwargs={"lazy":"selectin"})


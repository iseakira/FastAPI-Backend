from pydantic import EmailStr
from sqlalchemy import ARRAY,INTEGER
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
  created_at:datetime = Field(
      sa_column = Column(
         postgresql.TIMESTAMP,
         default=datetime.now,
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

  delivery_partner_id:UUID = Field(foreign_key="delivery_partner.id")
  delivery_partner:"DeliveryPartner" = Relationship(
     back_populates ="shipments",
     sa_relationship_kwargs={"lazy":"selectin"}

  )

class User(SQLModel,table=False):

      name:str
      email:EmailStr
      password_hash:str=Field(exclude=True)
class Seller(User, table=True):
   __tablename__="seller"

   id:UUID=Field(
     sa_column=Column(
        ## UUIDの扱いはDBごとに違うので明示
        postgresql.UUID,
        ##UUIDの生成ルールを関数で与えてる
        default=uuid4,
        primary_key=True,
     )
  )
   created_at:datetime = Field(
      sa_column = Column(
         postgresql.TIMESTAMP,
         default=datetime.now,
      )
   )
   shipments:list[Shipment]=Relationship(
      back_populates="seller",
      sa_relationship_kwargs={"lazy":"selectin"})

class DeliveryPartner(User,table=True):
   __tablename__="delivery_partner"
   id:UUID=Field(
      sa_column=Column(
        ## UUIDの扱いはDBごとに違うので明示
        postgresql.UUID,
        ##UUIDの生成ルールを関数で与えてる
        default=uuid4,
        primary_key=True,
     )
  )
   created_at:datetime = Field(
      sa_column = Column(
         postgresql.TIMESTAMP,
         default=datetime.now,
      )
   )
   serviceable_zip_codes:list[int] = Field(
      sa_column = Column(ARRAY(INTEGER))
   )
   max_handling_capacity:int
   shipments : list[Shipment] = Relationship(
      back_populates="delivery_partner",
      sa_relationship_kwargs={"lazy":"selectin"}
   )





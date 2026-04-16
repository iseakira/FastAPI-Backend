from pydantic import EmailStr
from sqlalchemy import ARRAY,INTEGER, select
from sqlmodel import Column, Relationship, SQLModel,Field
from uuid import uuid4,UUID
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects import postgresql


class ShipmentStatus(str,Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"

class TagName(str,Enum):
    EXPRESS="express"
    STANDARD="standard"
    FRAGILE="fragile"
    HEAVY = "heavy"
    INTERNATIONAL="international"
    DOMESTIC="domestic"
    TEMPRATURE_CONTROLLED="temperature_controlled"
    GIFT="gift"
    RETURN="return"
    DOCUMENTS="documents"

    async def tag(self,session:AsyncSession):
        return await session.scalar(
            select(Tag).where(Tag.name==self.value)
        )





class ShipmentTag(SQLModel, table=True):
  ## primary_keyが二つともTruなのはshipment_id + tag_id の組み合わせがユニークであるべきだから
  __tablename__="shipment_tag"

  shipment_id:UUID = Field(
      foreign_key="shipment.id",
      primary_key=True,

  )
  tag_id:UUID = Field(
      foreign_key="tag.id",
      primary_key=True,

  )


class Tag(SQLModel, table=True):
  __tablename__="tag"

  id:UUID = Field(
     sa_column=Column(
        ## UUIDの扱いはDBごとに違うので明示
        postgresql.UUID,
        ##UUIDの生成ルールを関数で与えてる
        default=uuid4,
        primary_key=True,
     )
  )

  name:TagName
  instruction:str

  shipments:list["Shipment"] = Relationship(
      back_populates="tags",
      link_model=ShipmentTag,
      sa_relationship_kwargs={"lazy":"immediate"},
  )

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
  client_contact_email:EmailStr
  client_contact_phone:str | None
  content:str
  weight:float = Field(le=25)

  timeline:list["ShipmentEvent"] = Relationship(
      back_populates = "shipment"
  )

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

  review: "Review" = Relationship(
      back_populates="shipment",
      sa_relationship_kwargs={"lazy":"selectin"},
  )
  tags: list[Tag] = Relationship(
      back_populates="shipments",
      link_model=ShipmentTag,
      sa_relationship_kwargs={"lazy":"immediate"},
  )

  orders: list["Order"] = Relationship(
      back_populates = "shipments",
  )

  def status(self):
      self.timeline[-1].status
      return self.timeline[-1].status if len(self.timeline) > 0 else None


class ShipmentEvent(SQLModel,table=True):
    __tablename__= "shipment_event"

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
    location:int
    status:ShipmentStatus
    description:str | None = Field(default = None)
    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment:Shipment=Relationship(
        back_populates = "timeline",
        sa_relationship_kwargs={"lazy":"selectin"}
    )


class User(SQLModel,table=False):

      name:str
      email:EmailStr
      email_verified:bool = Field(default=False)
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

   address:str
   zip_code:int

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

   @property
   def active_shipments(self):
       return [
           shipment
           for shipment in self.shipments

           if shipment.status != ShipmentStatus.delivered
           or shipment.status != ShipmentStatus.cancelled
       ]
   @property
   def current_handling_capacity(self):
       return self.max_handling_capacity-len(self.active_shipments)



class Review(SQLModel, table=True):
    __tablename__ = "review"

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

    rating: int = Field(ge=1,le=5)
    comment:str | None = Field(default=None)

    shipment_id:UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="review",
        sa_relationship_kwargs={"lazy":"selectin"},
    )


class Order(SQLModel,table=True):
    shipment_id:UUID = Field(foreign_key="shipment.id",primary_key=True)
    product_id:UUID = Field(foreign_key="product.id",primary_key=True)

    created_at:datetime
    quantity:int = Field(default=1)

    shipment: "Shipment" = Relationship(
        back_populates="orders"
    )

    product:"Product" = Relationship(
        back_populates = "orders"
    )

class Product(SQLModel, table=True):
    id:UUID = Field(default=None, primary_key=True,)
    title:str
    description:str
    price:float
    weight:float

    order:list["Order"] = Relationship(
        back_populates="products",
    )


shipment = Shipment()





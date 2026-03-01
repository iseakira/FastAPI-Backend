from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.database.session import get_session
from app.services.seller import SellerService
from app.services.shipment import ShipmentService
from app.core.security import oauth2_scheme_seller,oauth2_scheme_partner
from app.utils import decode_access_token




## Session sessiondep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def get_shipment_service(session:SessionDep):
  return ShipmentService(session)

async def get_seller_service(session:SessionDep):
  return SellerService(session)


##general function
async def _get_access_token(token:str)-> dict:
   data= decode_access_token(token)
   if data is None or await is_jti_blacklisted(data["jti"]):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid access token"
    )
   return data

## Seller access token data
async def get_seller_access_token(token:Annotated[str,Depends(oauth2_scheme_seller)]):
  return await _get_access_token(token)

async def get_partner_access_token(token:Annotated[str,Depends(oauth2_scheme_partner)]):
  return await _get_access_token(token)

##login seller
async def get_current_seller(
    token_data:Annotated[dict,Depends(get_seller_access_token)],
    session:SessionDep):
  seller=await session.get(Seller,UUID(token_data["user"]["id"]))
  if seller is None:
    raise HTTPException(
      sstaus_code = status.HTTP_401_UNAUTHORIZED,
      detail="Not Authorized"
    )
  return seller

## login partner
async def get_current_partner(
    token_data:Annotated[dict,Depends(get_partner_access_token)],
    session:SessionDep):
  partner=await session.get(DeliveryPartner,UUID(token_data["user"]["id"]))
  if partner is None:
    raise HTTPException(
      sstaus_code = status.HTTP_401_UNAUTHORIZED,
      detail="Not Authorized"
    )
  return partner






##Shipement Servicedep annotation
ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

##Seller Servicedep annotation
SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

## Seller Dep annotation
SellerDep = Annotated[Seller,Depends(get_current_seller)]

## Delivery Partner Dep annotation
DeliveryPartnerDep = Annotated[DeliveryPartner,Depends(get_current_partner)]



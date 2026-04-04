from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.database.redis import add_jti_to_blacklist

from ..schemas.delivery_partner import DeliveryPartnerRead, DeliveryPartnerCreate, DeliveryPartnerUpdate
from app.api.dependencies import DeliveryPartnerDep, DeliveryPartnerServiceDep, get_partner_access_token


router = APIRouter(prefix="/partner",tags=["Delivery Partner"])

### Verify Seller Email
@router.get("/verify")
async def verify_seller_email(token:str,service:DeliveryPartnerDep):
  await service.verify_email(token)
  return {"detail":"Account verified"}

@router.post("/signup",response_model=DeliveryPartnerRead)
async def register_delivery_partner(seller:DeliveryPartnerCreate,service:DeliveryPartnerServiceDep):
  return await service.add(seller)

# emailアドレスとパスワードを入力することでJWTトークンが返ってくる、
# requestformはOAuth2PasswordRequestFormに依存
# formdataのパースやoauth2_schemeと連携してBearer認証が可能
@router.post("/token")
async def login_delivery_partner(
  request_form:Annotated[OAuth2PasswordRequestForm,Depends()],
  service:DeliveryPartnerServiceDep,
  ):
  token=await service.token(request_form.username, request_form.password)
  return {
    "access_token":token,
    "type":"bearer",
  }

## Update Delivery Partner
@router.post("/",response_model=DeliveryPartnerUpdate)
async def update_delivery_partner(
  partner_update:DeliveryPartnerUpdate,
  partner:DeliveryPartnerDep,
  service:DeliveryPartnerServiceDep,
):
  return await service.update(
      partner.sqlmodel_update(partner_update)
  )


## ログアウト
@router.get("/logout")
async def logout_delivery_partner(token_data:Annotated[dict,Depends(get_partner_access_token)]):
  ##token_dataのuniqueIDをRedisのblacklistにぶち込んでる
  await add_jti_to_blacklist(token_data["jti"])
  return {
    "detail":"Success logout"
  }





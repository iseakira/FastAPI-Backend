from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.seller import SellerRead, SellerCreate
from app.api.dependencies import SellerServiceDep, get_access_token


router = APIRouter(prefix="/seller",tags=["Seller"])

@router.post("/signup",response_model=SellerRead)
async def register_seller(seller:SellerCreate,service:SellerServiceDep):
  return await service.add(seller)

# emailアドレスとパスワードを入力することでJWTトークンが返ってくる、
# requestformはOAuth2PasswordRequestFormに依存
# formdataのパースやoauth2_schemeと連携してBearer認証が可能
@router.post("/token")
async def login_seller(
  request_form:Annotated[OAuth2PasswordRequestForm,Depends()],
  service:SellerServiceDep,
  ):
  token=await service.token(request_form.username, request_form.password)
  return {
    "access_token":token,
    "type":"bearer",
  }

## ログアウト
@router.get("/logout")
async def logput_seller(token_data:Annotated[dict,Depends(get_access_token)]):
  token_data









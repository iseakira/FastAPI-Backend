from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from app.config import app_settings

from app.database.redis import add_jti_to_blacklist
from app.utils import TEMPLATE_DIR

from ..schemas.seller import SellerRead, SellerCreate
from app.api.dependencies import SellerServiceDep, get_seller_access_token


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

### Verify Seller Email
@router.get("/verify")
async def verify_seller_email(token:str,service:SellerServiceDep):
  await service.verify_email(token)
  return {"detail":"Account verified"}

### email password reset
@router.get("/forgot_password")
async def forgot_password(email: EmailStr,service: SellerServiceDep):
  await service.send_passwprd_reset_link(email,router.prefix)
  return {"detail":"Check email for password reset link"}

## Password Reset Form
@router.get("/reset_password_form")
async def get_reset_password_form(request:Request,token:str):
  templates= Jinja2Templates(TEMPLATE_DIR)

  return templates.TemplateResponse(
    request=request,
    name="reset_password.html",
    context={
      "reset_url":f"http://{app_settings.APP_DOMAIN}{router.prefix}/reset_password?token={token}"
    }
  )

### reset seller password
@router.post("/reset_password")
async def reset_password(
  request:Request,
  token:str,
  password:Annotated[str,Form()] = "",
  service: SellerServiceDep = None):

  is_success=await service.reset_password(token,password)

  templates = Jinja2Templates(TEMPLATE_DIR)

  return templates.TemplateResponse(
    request = request,
    name = "password/reset_password_success.html" if is_success else "password/reset_password_failed.html",

  )


## ログアウト
@router.get("/logout")
async def logout_seller(token_data:Annotated[dict,Depends(get_seller_access_token)]):
  ##token_dataのuniqueIDをRedisのblacklistにぶち込んでる
  await add_jti_to_blacklist(token_data["jti"])
  return {
    "detail":"Success logout"
  }









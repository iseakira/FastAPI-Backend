from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm

from app.database.models import Seller
from app.utils import decode_access_token
from ..schemas.seller import SellerRead, SellerCreate
from app.api.dependencies import SellerServiceDep, SessionDep
from app.core.security import oauth2_scheme

router = APIRouter(prefix="/seller",tags=["Seller"])

@router.post("/signup",response_model=SellerRead)
async def register_seller(seller:SellerCreate,service:SellerServiceDep):
  return await service.add(seller)

# emailアドレスとパスワードを入力することでJWTトークンが返ってくる、
# requestformはOAuth2PasswordRequestFormに依存
# formdataのパースやoauth2_schemeと連携してBarer認証が可能
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

@router.get("/dashboard")
async def get_dashboard(
  token:Annotated[str,Depends(oauth2_scheme)],
  session: SessionDep,
  ):
  data= decode_access_token(token)

  if data is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid access token"
    )
  seller = await session.get(Seller,data["user"]["id"])
  return seller






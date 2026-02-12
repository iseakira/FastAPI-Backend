from fastapi import APIRouter
from ..schemas.seller import SellerRead, SellerCreate
from app.api.dependencies import SellerServiceDep

router = APIRouter(prefix="/seller",tags=["Seller"])

@router.post("/signup",response_model=SellerRead)
async def register_seller(seller:SellerCreate,service:SellerServiceDep):
  return await service.add(seller)

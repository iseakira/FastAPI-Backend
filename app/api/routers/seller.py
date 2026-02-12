from fastapi import APIRouter
from ..schemas.seller import SellerCreate

router = APIRouter(prefix="seller/")

@router.post("/")
def register_seller(seller:SellerCreate):
  pass

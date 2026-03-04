
from .routers import shipment, seller,deliver_partner
from fastapi import APIRouter

master_router = APIRouter()

master_router.include_router(shipment.router)
master_router.include_router(seller.router)
master_router.include_router(deliver_partner.router)
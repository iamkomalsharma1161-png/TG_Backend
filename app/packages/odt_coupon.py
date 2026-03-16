from fastapi import APIRouter , Depends , HTTPException 
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ODTCoupon
import random
import string 

router = APIRouter()

ALLOWED_PROMO = "NIDHI2203"

def generate_coupon_code():
    return "TG" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.post("/generate_coupon")
def generate_coupon(promo : str , db : Session = Depends(get_db)):

    if promo != ALLOWED_PROMO:
        raise HTTPException(status_code=400, detail="Invalid promo code")

    code = generate_coupon_code()

    coupon = ODTCoupon(
        coupon_code = code,
        discount = 50, 
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    return{
        "coupon_code":coupon.coupon_code,
        "discount": coupon.discount
    }
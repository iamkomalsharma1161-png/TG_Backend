from fastapi import FastAPI ,  HTTPException , Response , status , Depends , APIRouter , Form , File , UploadFile 
import json
import uuid
from app import models , schema  
from sqlalchemy.orm import Session
from app.database import engine , get_db
from app.config import settings  
from app.utils.mail.odt_mail import send_booking_email , send_email_with_invoice , send_booking_declined_email 
# , send_admin_booking_mail
import shutil, os
from fastapi import BackgroundTasks
from app.utils.invoice_generator import generate_invoice
from app.utils.supabase_uploads import upload_to_supabase


router = APIRouter()

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# @router.post("/odt_booking" , status_code = status.HTTP_201_CREATED)
# async def odt_booking( background_tasks: BackgroundTasks,
#     full_name: str = Form(...),
#     email_address: str = Form(...),
#     age: int = Form(...),
#     gender: str = Form(...),
#     contact_number: str = Form(...),
#     whatsapp_number: str = Form(...),
#     college_name: str = Form(...),
#     pick_up_loc: str = Form(...),
#     drop_loc: str = Form(...),
#     meal_preference: str = Form(...),
#     trip_exp_level: str = Form(None),
#     medical_details: str = Form(None),
#     agree: bool = Form(...),
#     coupon_code:str = Form(None),
#     payment_screenshot: UploadFile = File(None),  db:Session = Depends(get_db) 
   
# ):

#     # discount = 0 

#     # if coupon_code and coupon_code.strip():
#     #     coupon = db.query(models.ODTCoupon).filter(
#     #         models.ODTCoupon.coupon_code == coupon_code
#     #     ).first()
#     #     if not coupon:
#     #         raise HTTPException(status_code=400, detail="Invalid coupon code")
#     #     if coupon.used:
#     #         raise HTTPException(status_code=400, detail="Coupon code already used")
#     #     discount = coupon.discount

#     file_location = None

#     if payment_screenshot:
#         file_name = f"{email_address}_payment_{payment_screenshot.filename}"
#         file_location = os.path.join(UPLOAD_DIR, file_name)
#         with open(file_location, "wb") as buffer:
#             shutil.copyfileobj(payment_screenshot.file, buffer)
#     # payment_screenshot_url = None
#     # if payment_screenshot:
#     #     payment_screenshot_url = upload_to_supabase(
#     #         payment_screenshot,
#     #         folder="odt_B7_payments"
#     #     )
    
#     details = models.ODT(
#         full_name=full_name,
#         email_address=email_address,
#         age=age,
#         gender=gender,
#         contact_number=contact_number,
#         whatsapp_number=whatsapp_number , 
#         college_name=college_name,
#         pick_up_loc=pick_up_loc,
#         drop_loc=drop_loc,
#         meal_preference=meal_preference,
#         trip_exp_level=trip_exp_level,
#         medical_details=medical_details,
#         agree=agree,
#         payment_screenshot=file_location
#     ) 
   
    
  
#     db.add(details) 
#     db.commit() 
#     db.refresh(details)

#     # if coupon_code:
#     #     coupon.used = True 
#     #     coupon.used_by_email = email_address
#     #     db.commit()

#     # invoice_path = generate_invoice(details)

#     background_tasks.add_task(send_booking_email, details , file_location)
#     # background_tasks.add_task(send_email_with_invoice, details, invoice_path)

#     return {"message" : "Payment Successful"}

def get_price_per_person(total_people: int) -> int:
    if total_people <= 3:
        return 1301
    elif total_people <= 5:
        return 1275
    else:
        return 1251

# @router.post("/odt_booking", status_code=status.HTTP_201_CREATED)
# async def odt_booking(
#     background_tasks: BackgroundTasks,
#     travellers: str = Form(...),   # JSON string array
#     meal_preference: str = Form(...),
#     agree: bool = Form(...),
#     payment_screenshot: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     # Parse travellers JSON
#     travellers_list = json.loads(travellers)
#     print("PARSED:", travellers_list)
#     print(type(travellers_list))
#     try:
#         print("RAW travellers:", travellers)
#         print(type(travellers))
#         travellers_list = json.loads(travellers)

#         if not isinstance(travellers_list, list):
#             raise ValueError("Travellers must be a list")

#     except Exception:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid travellers data"
#         )

#     total_people = len(travellers_list)

#     if total_people == 0:
#         raise HTTPException(
#             status_code=400,
#             detail="At least one traveller required"
#         )

#     price_per_person = get_price_per_person(total_people)
#     total_price = price_per_person * total_people

#     if not total_price:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid group size"
#         )

#     # Save screenshot
#     file_location = None

#     if payment_screenshot:
#         unique_id = uuid.uuid4().hex
#         file_name = f"booking_{unique_id}_{payment_screenshot.filename}"
#         file_location = os.path.join(UPLOAD_DIR, file_name)

#         with open(file_location, "wb") as buffer:
#             shutil.copyfileobj(payment_screenshot.file, buffer)
#     primary_email = travellers_list[0]["email_address"]
#     # Create booking
#     booking = models.ODT1(
#         primary_email=primary_email,
#         total_people=total_people,
#         total_price=total_price,
#         meal_preference=meal_preference,
#         agree=agree,
#         payment_screenshot=file_location,
#         status="pending"
#     )

#     db.add(booking)
#     db.commit()
#     db.refresh(booking)

#     # Add travellers
#     for traveller in travellers_list:
#         traveller_data = models.ODTTraveller(
#             booking_id=booking.id,
#             full_name=traveller["full_name"],
#             email_address=traveller["email_address"],
#             age=traveller["age"],
#             gender=traveller["gender"],
#             contact_number=traveller["contact_number"],
#             whatsapp_number=traveller["whatsapp_number"],
#             college_name=traveller["college_name"],
#             pick_up_loc=traveller["pick_up_loc"],
#             drop_loc=traveller["drop_loc"],
#             trip_exp_level=traveller.get("trip_exp_level"),
#             medical_details=traveller.get("medical_details")
#         )

#         db.add(traveller_data)


#     db.commit()

#     background_tasks.add_task(
#     send_admin_booking_mail,
#     booking.id,
#     db
#     )

#     return {
#         "message": "Booking successful",
#         "booking_id": booking.id,
#         "total_people": total_people,
#         "total_price": total_price
#     }
@router.post("/odt_booking" , status_code = status.HTTP_201_CREATED)
async def odt_booking( background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email_address: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    contact_number: str = Form(...),
    whatsapp_number: str = Form(...),
    college_name: str = Form(...),
    pick_up_loc: str = Form(...),
    drop_loc: str = Form(...),
    meal_preference: str = Form(...),
    trip_exp_level: str = Form(None),
    medical_details: str = Form(None),
    agree: bool = Form(...),
    coupon_code:str = Form(None),
    payment_screenshot: UploadFile = File(None),  db:Session = Depends(get_db) 
   
):

    # discount = 0 

    # if coupon_code and coupon_code.strip():
    #     coupon = db.query(models.ODTCoupon).filter(
    #         models.ODTCoupon.coupon_code == coupon_code
    #     ).first()
    #     if not coupon:
    #         raise HTTPException(status_code=400, detail="Invalid coupon code")
    #     if coupon.used:
    #         raise HTTPException(status_code=400, detail="Coupon code already used")
    #     discount = coupon.discount

    file_location = None

    if payment_screenshot:
        file_name = f"{email_address}_payment_{payment_screenshot.filename}"
        file_location = os.path.join(UPLOAD_DIR, file_name)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(payment_screenshot.file, buffer)
    # payment_screenshot_url = None
    # if payment_screenshot:
    #     payment_screenshot_url = upload_to_supabase(
    #         payment_screenshot,
    #         folder="odt_B7_payments"
    #     )
    
    details = models.ODT(
        full_name=full_name,
        email_address=email_address,
        age=age,
        gender=gender,
        contact_number=contact_number,
        whatsapp_number=whatsapp_number , 
        college_name=college_name,
        pick_up_loc=pick_up_loc,
        drop_loc=drop_loc,
        meal_preference=meal_preference,
        trip_exp_level=trip_exp_level,
        medical_details=medical_details,
        agree=agree,
        payment_screenshot=file_location
    ) 
   
    
  
    db.add(details) 
    db.commit() 
    db.refresh(details)

    # if coupon_code:
    #     coupon.used = True 
    #     coupon.used_by_email = email_address
    #     db.commit()

    # invoice_path = generate_invoice(details)

    background_tasks.add_task(send_booking_email, details , file_location)
    # background_tasks.add_task(send_email_with_invoice, details, invoice_path)

    return {"message" : "Payment Successful"}


@router.get("/odt/confirm")
async def confirm_amount(booking_id: int, amount: int, db: Session = Depends(get_db)):
    # Fetch booking
    booking = db.query(models.ODT).filter(models.ODT.id == booking_id).first()

    if not booking:
        return {"error": "Booking not found"}

    # Generate invoice with selected amount
    print(amount , type(amount))
    invoice_path = generate_invoice(booking, amount)

    # Send invoice to user
    await send_email_with_invoice(booking, invoice_path)

    return {"message": f"Invoice for ₹{amount} sent to user {booking.email_address}"}

@router.get("/odt/decline")
async def decline_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    # Fetch booking
    booking_data = db.query(models.ODT).filter(models.ODT.id == booking_id).first()

    if not booking_data:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Send decline email
    await send_booking_declined_email(booking_data)

    return {
        "status": "declined",
        "message": "User notified about payment not received."
    }
# @router.get("/odt/approve")
# def approve_booking(
#     booking_id: int,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)
# ):
#     booking = db.query(models.ODT1).filter(
#         models.ODT1.id == booking_id
#     ).first()

#     if not booking:
#         raise HTTPException(404, "Booking not found")
#     invoice_path = generate_invoice(booking, amount)

#     booking.status = "approved"

#     db.commit()

#     background_tasks.add_task(
#         send_approval_mail_to_user,
#         booking.primary_email,
#         invoice_path,
#         booking
#     )

#     return {"message": "Booking approved"}

# @router.get("/decline")
# def decline_booking(
#     booking_id: int,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)
# ):
#     booking = db.query(models.ODT1).filter(
#         models.ODT1.id == booking_id
#     ).first()

#     if not booking:
#         raise HTTPException(404, "Booking not found")

#     booking.status = "declined"

#     db.commit()

#     background_tasks.add_task(
#         send_decline_mail_to_user,
#         booking.primary_email,
#         booking
#     )

#     return {"message": "Booking declined"}

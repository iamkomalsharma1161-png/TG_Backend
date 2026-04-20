from fastapi import FastAPI ,  HTTPException , Response , status , Depends , APIRouter , Form , File , UploadFile 
from typing import List
from app import models , schema 
from sqlalchemy.orm import Session
from app.database import engine , get_db
from app.config import settings  
from app.utils.mail.pachmarhi_mail import send_booking_email , send_email_with_invoice, send_booking_declined_email
import shutil, os
from fastapi import BackgroundTasks
from app.utils.supabase_uploads import upload_to_supabase
import json
from app.utils.pricing.pachmarhi import get_price_per_person
from app.utils.invoice_generator import generate_invoice_pachmarhi


router = APIRouter()

@router.post("/pachmarhi_booking", status_code=status.HTTP_201_CREATED)
async def pachmarhi_booking(
    background_tasks: BackgroundTasks,
    travellers: str = Form(...),
    meal_preference: str = Form(...),
    sharing_preference: str = Form(...),
    payment_option: str = Form(...),
    agree: bool = Form(...),
    payment_screenshot: UploadFile = File(...),
    id_images: List[UploadFile] = File(...),   # FIX 1: Accept id images per traveller
    db: Session = Depends(get_db)
):
    # FIX 2: Parse travellers JSON only once
    try:
        travellers_list = json.loads(travellers)
        if not isinstance(travellers_list, list):
            raise ValueError("Travellers must be a list")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid travellers data")

    total_people = len(travellers_list)

    if total_people == 0:
        raise HTTPException(status_code=400, detail="At least one traveller required")

    # FIX 3: Validate id_images count matches travellers
    if len(id_images) != total_people:
        raise HTTPException(status_code=400, detail="Each traveller must have an ID image")
   
    price_per_person = get_price_per_person(total_people, meal_preference , sharing_preference)
    total_price = price_per_person * total_people
    if payment_option == "partial":
        total_price = total_price / 2
    print(total_price)

    if not total_price:
        raise HTTPException(status_code=400, detail="Invalid group size")

    payment_screenshot_url =  upload_to_supabase(
        payment_screenshot,
        folder="pachmarhi_payments"
    )

    primary_email = travellers_list[0]["email_address"]
    primary_traveller_name = travellers_list[0]["full_name"]
    primary_traveller_contact = travellers_list[0]["contact_number"]

    booking = models.Pachmarhi(
        primary_email=primary_email,
        primary_traveller_name=primary_traveller_name,
        primary_traveller_contact=primary_traveller_contact,
        total_people=total_people,
        total_price=total_price,
        meal_preference=meal_preference,
        sharing_preference=sharing_preference,  # FIX 4: Match the typo in your model column
        payment_option=payment_option,         # FIX 5: Match singular column name in model
        agree=agree,
        payment_screenshot=payment_screenshot_url,
        status="pending"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # FIX 6: Move id_image upload outside constructor, pair each image with its traveller
    for traveller, id_image in zip(travellers_list, id_images):
        id_image_url =  upload_to_supabase(
            id_image,
            folder="pachmarhi_id_images"
        )

        traveller_data = models.PachmarhiTraveller(
            booking_id=booking.id,
            full_name=traveller["full_name"],
            email_address=traveller["email_address"],
            age=traveller["age"],
            gender=traveller["gender"],
            contact_number=traveller["contact_number"],
            whatsapp_number=traveller["whatsapp_number"],
            emergency_contact_number=traveller["emergency_contact_number"],
            college_name=traveller["college_name"],
            trip_exp_level=traveller.get("trip_exp_level"),
            medical_details=traveller.get("medical_details"),
            id_image=id_image_url   # FIX 7: Now correctly passed in
        )
        db.add(traveller_data)

    db.commit()

    # FIX 8: Remove undefined `file_location` argument
    background_tasks.add_task(
        send_booking_email,
        booking.id,
        db ,  
        payment_screenshot_url
    )

    return {
        "message": "Booking successful",
        "booking_id": booking.id,
        "total_people": total_people,
        "total_price": total_price
    }

@router.get("/pachmarhi/approve")
def approve_booking(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    booking = db.query(models.Pachmarhi).filter(
        models.Pachmarhi.id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(404, "Booking not found")
    invoice_path = generate_invoice_pachmarhi(booking)
    if booking.payment_option == "full_payment":
        booking.status = "approved"

    db.commit()

    background_tasks.add_task(
        send_email_with_invoice,
        booking.primary_email,
        booking,
        invoice_path
    )

    return {"message": "Booking approved"}

@router.get("/pachmarhi/decline")
def decline_booking(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    booking = db.query(models.Pachmarhi).filter(
        models.Pachmarhi.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    booking.status = "declined"

    db.commit()

    background_tasks.add_task(
        send_booking_declined_email,
        booking,
        booking.primary_email
    )

    return {"message": "Booking declined"}

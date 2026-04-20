from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, SupportQuery, Notification, ODT, ODT1, ManaliTripBooking, VRDarshanBooking, BhajanJamming
from ..schemas_userpanel import UserProfileUpdate, UserResponse, SupportQueryCreate, SupportQueryResponse, NotificationResponse
from .auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["User Panel"])

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(profile_data: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.age is not None:
        current_user.age = profile_data.age
    if profile_data.city is not None:
        current_user.city = profile_data.city
    if profile_data.emergency_contact_name is not None:
        current_user.emergency_contact_name = profile_data.emergency_contact_name
    if profile_data.emergency_contact_number is not None:
        current_user.emergency_contact_number = profile_data.emergency_contact_number
    if profile_data.profile_photo_url is not None:
        current_user.profile_photo_url = profile_data.profile_photo_url
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/bookings")
def get_my_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find bookings matching email
    email = current_user.email_address

    # ODT Bookings
    odt_bookings = db.query(ODT).filter(ODT.email_address == email).all()
    # ODT1 Bookings
    odt1_bookings = db.query(ODT1).filter(ODT1.primary_email == email).all()
    # Manali
    manali_bookings = db.query(ManaliTripBooking).filter(ManaliTripBooking.email == email).all()
    
    auth_trips = []
    for b in odt_bookings:
        date_str = b.submitted_at.strftime("%d %b %Y") if b.submitted_at else "N/A"
        auth_trips.append({"type": "General ODT", "destination": b.drop_loc or "Trek", "date": date_str, "status": "Paid" if b.payment_screenshot else "Pending", "id": b.id})
    for b in odt1_bookings:
        date_str = b.submitted_at.strftime("%d %b %Y") if b.submitted_at else "N/A"
        auth_trips.append({"type": "Premium ODT", "destination": "Custom Premium Trip", "date": date_str, "status": b.status or "Pending", "id": b.id})
    for b in manali_bookings:
        date_str = b.created_at.strftime("%d %b %Y") if b.created_at else "N/A"
        auth_trips.append({"type": "Manali Trip", "destination": "Manali", "date": date_str, "status": "Paid" if b.payment_screenshot else "Pending", "id": b.id})

    # Divya Drishti (VR)
    vr_bookings = db.query(VRDarshanBooking).filter(VRDarshanBooking.email_address == email).all()
    vr_list = []
    for v in vr_bookings:
        date_str = v.preferred_date.strftime("%d %b %Y") if v.preferred_date else "N/A"
        vr_list.append({"type": "Divya Drishti", "date": date_str, "time_slot": v.time_slot, "status": v.booking_status, "id": v.id})

    # Bhajan Jamming (Still using phone since model doesn't have email)
    phone = current_user.contact_number
    bhajan_list = []
    if phone:
        bhajan = db.query(BhajanJamming).filter(BhajanJamming.contact_number == phone).all()
        for b in bhajan:
            bhajan_list.append({"type": "Bhajan Jamming", "date": b.submitted_at, "id": b.id})

    return {
        "trips": auth_trips,
        "divya_drishti": vr_list,
        "bhajan_jamming": bhajan_list
    }

@router.post("/support", response_model=SupportQueryResponse)
def create_support_query(query: SupportQueryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_query = SupportQuery(
        user_id=current_user.id,
        subject=query.subject,
        query_text=query.query_text,
        photo_url=query.photo_url
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    return new_query

@router.get("/support")
def get_support_queries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    queries = db.query(SupportQuery).filter(SupportQuery.user_id == current_user.id).all()
    return queries

@router.get("/notifications")
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return notifications

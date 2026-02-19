import json , shutil , os , qrcode , uuid , tempfile
from fastapi import HTTPException
from app.utils.supabase_uploads import upload_to_supabase_qr
from fastapi import FastAPI ,  HTTPException , Response , status , Depends , APIRouter , Form , File , UploadFile
from app import models , schema  
from sqlalchemy.orm import Session
from app.database import engine , get_db
from app.config import settings 
from fastapi import BackgroundTasks

router = APIRouter()
def generate_payment_qr(amount: int) -> str:
    upi_id = "6260499299@okbizaxis"
    payee_name = "Tirth Ghumo"
    

    upi_url = (
        f"upi://pay?"
        f"pa={upi_id}"
        f"&pn={payee_name}"
        f"&am={amount}"
        f"&cu=INR"
        
    )

    qr = qrcode.make(upi_url)

    filename = f"vr_darshan_qr_{uuid.uuid4()}.png"

    # ✅ cross-platform temp directory
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    qr.save(file_path)

    return file_path

CHAR_DHAM = [
    "Kedarnath", "Badrinath", "Gangotri", "Yamunotri"
]

JYOTIRLINGA = [
    "Somnath", "Mallikarjuna", "Mahakaleshwar",
    "Omkareshwar", "Kedarnath Jyotirlinga",
    "Bhimashankar", "Kashi Vishwanath",
    "Trimbakeshwar", "Vaidyanath", "Nageshwar"
]

ABHISHEK_3D = [
    "Mahakal 3D Abhishek",
    "Kashi Vishwanath 3D",
    "Somnath 3D",
    "Omkareshwar 3D"
]

SHAKTIPEETH = [
    "Vaishno Devi", "Kamakhya Devi",
    "Kalighat", "Jwala Ji",
    "Chintpurni", "Hinglaj Mata",
    "Maa Tara Tarini", "Maa Sharda"
]

@router.get("/vr-darshan/price")
async def generate_vr_darshan_qr(
    devotees: str = Form(...)
):
    try:
        devotees_data = json.loads(devotees)
    except Exception:
        raise HTTPException(400, "Invalid devotees JSON")

    total_amount = 0

    for devotee in devotees_data:

        category = devotee.get("category")
        selected_temples = devotee.get("spiritual_places")

        if not category or not selected_temples:
            raise HTTPException(400, "Category and spiritual_places required")

        # Expand "All Temples"
        if "All Temples" in selected_temples:
            if category == "Char Dham":
                selected_temples = CHAR_DHAM
            elif category == "Jyotirlinga & Shiv Darshan":
                selected_temples = JYOTIRLINGA
            elif category == "3D Abhishek Darshan":
                selected_temples = ABHISHEK_3D
            elif category == "Shaktipeeth & Devi Darshan":
                selected_temples = SHAKTIPEETH

        count = len(selected_temples)

        # 🔥 Pricing Logic

        if category == "Char Dham":
            total_amount += 151 if count == 4 else count * 51

        elif category == "Jyotirlinga & Shiv Darshan":
            if count == 10:
                total_amount += 451
            elif count == 6:
                total_amount += 251
            else:
                total_amount += count * 51

        elif category == "3D Abhishek Darshan":
            total_amount += 351 if count == len(ABHISHEK_3D) else count * 51

        elif category == "Shaktipeeth & Devi Darshan":
            total_amount += 401 if count == len(SHAKTIPEETH) else count * 51

        else:
            raise HTTPException(400, f"Invalid category {category}")

    qr_path = generate_payment_qr(total_amount)
    qr_url = upload_to_supabase_qr(qr_path, "vr_darshan_qr")

    return {
        "amount": total_amount,
        "payment_qr_url": qr_url
    }


@router.get("/manali/price")
async def calculate_manali_price(
    sleeper: int , 
    ac : int
):

    PRICE_PER_SLEPPER = 5000
    PRICE_PER_AC = 6000
    amount = (sleeper * PRICE_PER_SLEPPER) + (ac * PRICE_PER_AC)
    qr_path = generate_payment_qr(amount)
    qr_url = upload_to_supabase_qr(qr_path, "manali_qr")
    session_id = str(uuid.uuid4())

    return {
        "payment_qr_url": qr_url,
        "amount":amount , 
    }






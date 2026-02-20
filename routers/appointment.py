from fastapi import APIRouter, Depends
from database import database
from auth.jwt import get_current_user
from schemas.appointment_schema import AppointmentCreate, AppointmentResponse
from datetime import datetime
from fastapi import HTTPException
from bson import ObjectId

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/")
async def create_appointment(
    payload: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    appointments = database["appointments"]

    # 🔍 Check if time slot already booked
    existing = await appointments.find_one({
        "appointment_time": payload.appointment_time
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This time slot is already booked"
        )

    doc = {
        "user_id": current_user["sub"],
        "service": payload.service,
        "appointment_time": payload.appointment_time,
        "created_at": datetime.utcnow()
    }

    await appointments.insert_one(doc)

    return {"message": "Appointment created successfully"}

@router.get("/my", response_model=list[AppointmentResponse])
async def get_my_appointments(
    current_user: dict = Depends(get_current_user)
):
    appointments = database["appointments"]

    user_appointments = await appointments.find(
        {"user_id": current_user["sub"]}
    ).to_list(100)

    result = []

    for appt in user_appointments:
        result.append(
            AppointmentResponse(
                id=str(appt["_id"]),
                service=appt["service"],
                appointment_time=appt["appointment_time"],
                created_at=appt["created_at"]
            )
        )

    return result




@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    appointments = database["appointments"]

    appointment = await appointments.find_one({
        "_id": ObjectId(appointment_id)
    })

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment["user_id"] != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this appointment")
    
    await appointments.delete_one({
        "_id": ObjectId(appointment_id)
        })
    return {"message": "Appointment cancelled successfully"}


@router.get("/all")
async def get_all_appointments(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    appointments = database["appointments"]

    all_appointments = await appointments.find().to_list(100)

    for appt in all_appointments:
        appt["_id"] = str(appt["_id"])

    return all_appointments

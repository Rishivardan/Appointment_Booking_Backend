from pydantic import BaseModel
from datetime import datetime

class AppointmentCreate(BaseModel):
    service: str
    appointment_time: datetime

class AppointmentResponse(BaseModel):
    id: str
    service: str
    appointment_time: datetime
    created_at: datetime
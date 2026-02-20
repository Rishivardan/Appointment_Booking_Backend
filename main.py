from fastapi import FastAPI
from database import database
from routers.auth import router as auth_router
from routers import appointment
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

# Include auth routes
app.include_router(auth_router)

# Include appointment routes
app.include_router(appointment.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Appointment Booking API!"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    
    for err in exc.errors():
        errors.append({
            "field": err["loc"][-1],
            "message": err["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "Validation Error",
                "details": errors
            }
        }
    )

origins = [
    "http://localhost:3000",  # React
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
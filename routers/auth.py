from fastapi import APIRouter, HTTPException, status
from database import database
from auth.hashing import hash_password, verify_password
from auth.jwt import create_access_token
from schemas.user_schema import UserRegister, UserLogin
from bson import ObjectId
from datetime import datetime
from fastapi import Depends
from auth.jwt import get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    try:
        users = database["users"]

        existing = await users.find_one({"email": payload.email.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # DEBUG: Print what we're about to hash
        print(f"DEBUG - Password to hash: {payload.password}")
        print(f"DEBUG - Password type: {type(payload.password)}")
        print(f"DEBUG - Password length: {len(payload.password)}")
        print(f"DEBUG - Password bytes: {len(payload.password.encode('utf-8'))}")
        
        # Hash the password
        password_hash = hash_password(payload.password)
        print(f"DEBUG - Hash successful: {password_hash[:50]}...")

        
        email = payload.email.lower()

        role = "admin" if email == "admin@example.com" else "customer"
        
        doc = {
            "name": payload.name,
            "email": email,
            "passwordHash": hash_password(payload.password),
            "role": role,
            "createdAt": datetime.utcnow()
        }

        result = await users.insert_one(doc)

        token = create_access_token({
            "sub": str(result.inserted_id),
            "email": doc["email"],
            "role": doc["role"]
        })

        return {"message": "Registered successfully", "access_token": token}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(payload: UserLogin):
    try:
        users = database["users"]
        user = await users.find_one({"email": payload.email.lower()})

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not verify_password(payload.password, user["passwordHash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = create_access_token({
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user.get("role", "customer")
        })

        return {"message": "Login successful", "access_token": token}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Token is valid",
        "user": current_user
    }


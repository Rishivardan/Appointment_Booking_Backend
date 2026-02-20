from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """
        Validate that password doesn't exceed 72 bytes.
        This is bcrypt's maximum password length.
        """
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError(
                f'Password is too long ({len(password_bytes)} bytes). '
                f'Maximum is 72 bytes. Please use a shorter password.'
            )
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
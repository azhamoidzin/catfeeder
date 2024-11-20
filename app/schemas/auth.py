from pydantic import BaseModel, EmailStr


class EncodeData(BaseModel):
    email: EmailStr

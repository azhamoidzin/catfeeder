from pydantic import BaseModel, EmailStr


class ActivationData(BaseModel):
    password: str


class NewMember(BaseModel):
    name: str
    email: EmailStr

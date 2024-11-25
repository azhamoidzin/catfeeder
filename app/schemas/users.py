from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    email: EmailStr
    name: str
    disabled: bool
    family_admin: bool
    family_id: int
    hashed_password: str | None = None


class UserInDB(User):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: datetime | None = None


class UserUpdate(BaseModel):
    disabled: None | bool = None
    email: None | EmailStr = None
    name: None | str = None
    hashed_password: None | str


class Token(BaseModel):
    access_token: str
    token_type: str

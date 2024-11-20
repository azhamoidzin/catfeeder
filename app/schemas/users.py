from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    email: EmailStr
    name: str
    disabled: bool
    family_admin: bool
    family_id: int
    registered_at: datetime | None = None
    hashed_password: str | None = None


class UserInDB(User):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserUpdate(BaseModel):
    id: int
    disabled: None | bool = None
    email: None | EmailStr = None
    name: None | str = None
    hashed_password: None | str


class Token(BaseModel):
    access_token: str
    token_type: str

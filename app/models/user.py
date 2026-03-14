from pydantic import BaseModel


class UserCreate(BaseModel):
    user_id: str
    name: str
    status: str = "active"


class UserUpdate(BaseModel):
    name: str | None = None
    status: str | None = None


class UserResponse(BaseModel):
    user_id: str
    name: str
    status: str

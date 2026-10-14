from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=6)
    display_name: str | None = None


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    user_id: int
    display_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    display_name: str
    is_guest: bool


class SessionCreate(BaseModel):
    title: str = "新会话"


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    size: int
    created_at: datetime


class TaskCreate(BaseModel):
    type: str = "generic"
    params: dict = {}
    status: str = "pending"


class TaskUpdate(BaseModel):
    status: str | None = None
    result: dict | None = None
    params: dict | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    type: str
    params: dict
    status: str
    result: dict | None
    created_at: datetime
    updated_at: datetime
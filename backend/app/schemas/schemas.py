from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 72:
            raise ValueError('Password must be 72 characters or fewer')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: Optional[datetime] = None  # 🔥 FIXED: Made optional so it doesn't crash

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class StockData(BaseModel):
    symbol: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    history: list


class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    direction: str
    change_percent: float


class SentimentResponse(BaseModel):
    symbol: str
    sentiment_label: str
    sentiment_score: float
    articles_analyzed: int
    headlines: list
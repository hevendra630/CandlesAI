from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
import datetime  # 🔥 FIXED: Added missing import
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 🔥 FIXED: Added python-side default to ensure timestamp exists immediately
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, server_default=func.now())
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="USER", nullable=False)  # "ADMIN", "USER"
    status = Column(String(20), default="active", nullable=False)  # "active", "inactive"
    auth_provider = Column(String(20), default="local", nullable=False)  # "local", "google"
    google_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    papers = relationship("ResearchPaper", back_populates="user", cascade="all, delete-orphan")
    history = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("InAppNotification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    name = Column(String)
    registered_at = Column(DateTime, default=datetime.utcnow)
    subscription_settings = Column(String)

    logs = relationship("Log", back_populates="user")

class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    command = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")
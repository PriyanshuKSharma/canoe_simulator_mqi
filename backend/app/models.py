import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from .database import Base

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # 'INFO', 'WARNING', 'ERROR'
    signals_snapshot = Column(Text, nullable=True)  # JSON-serialized snapshot of signals at event time
    ai_analysis = Column(Text, nullable=True)       # Store AI-generated failure analysis if requested

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

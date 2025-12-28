"""
Database models using SQLAlchemy ORM.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import settings

Base = declarative_base()


class AgentTable(Base):
    """Database model for Discord bot agents."""
    
    __tablename__ = "agents"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identity
    name = Column(String(255), nullable=False)
    discord_token = Column(String(255), nullable=False)
    discord_enabled = Column(Boolean, default=True, nullable=False, index=True)
    
    # Bot Identity (populated after connection)
    discord_bot_user_id = Column(String(255), nullable=True)
    discord_bot_username = Column(String(255), nullable=True)
    discord_bot_display_name = Column(String(255), nullable=True)
    
    # Response Settings
    respond_to_dm = Column(Boolean, default=True, nullable=False)
    
    # Whitelists (JSON arrays)
    guild_whitelist = Column(JSON, default=list, nullable=False)
    channel_whitelist = Column(JSON, default=list, nullable=False)
    
    # Agent Implementation
    agent_type = Column(String(50), default="echo", nullable=False)
    agent_config = Column(JSON, default=dict, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', enabled={self.discord_enabled})>"


# Database engine and session
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Get a database session (generator for dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

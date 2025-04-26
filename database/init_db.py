from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base
from utils.config import get_config

config = get_config()

# SQL Database setup
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./risk.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    Dependency function to provide a database session
    Usage in FastAPI:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Create the engine to connect to Dockerized Postgres
engine = create_engine(settings.DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()

# Dependency for FastAPI routes to access the DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
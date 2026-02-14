from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string - using SQLite for local development
# For production, set DATABASE_URL to a PostgreSQL connection string
# Supabase example: postgresql://postgres.[ref]:[pw]@aws-0-[region].pooler.supabase.com:6543/postgres
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aislides.db")

# Create engine with appropriate settings for SQLite or PostgreSQL
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL / Supabase configuration
    # - pool_pre_ping: detect stale connections after Supabase auto-pause (7 day idle)
    # - pool_recycle: refresh connections every 5 min to avoid stale pooled connections
    # - NullPool: required for Supavisor transaction mode (port 6543) which manages
    #   its own connection pooling — SQLAlchemy must not pool on top of it
    # - connect_args: 10s connect timeout to allow Supabase wake-up from pause
    use_nullpool = ":6543" in SQLALCHEMY_DATABASE_URL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        **({"poolclass": NullPool} if use_nullpool else {"pool_recycle": 300, "pool_size": 5}),
        connect_args={"connect_timeout": 10},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
SafeBite — Database Layer
Oracle connection via oracledb (thin mode) + SQLAlchemy ORM
"""

import oracledb
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN      = os.getenv("DB_DSN")



def _oracle_creator():
    """Raw oracledb connection factory used by SQLAlchemy."""
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


engine = create_engine(
    "oracle+oracledb://",
    creator=_oracle_creator,
    poolclass=NullPool,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ── Dependency injected into every route ─────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """Returns True if Oracle is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        return True
    except Exception as e:
        print(f"⚠️  Oracle connection failed: {e}")
        return False
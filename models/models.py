"""
SafeBite — SQLAlchemy Models
Maps exactly to the Oracle tables discovered in the DB inspection.
"""

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey, Text, func
)
from sqlalchemy.orm import relationship
from database.connection import Base


# ─────────────────────────────────────────────────────────────────────────────
#  USERS
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "USERS"

    user_id             = Column("USER_ID",              Integer, primary_key=True)
    username            = Column("USERNAME",             String(50),  unique=True, nullable=False)
    password            = Column("PASSWORD",             String(200), nullable=False)
    full_name           = Column("FULL_NAME",            String(100))
    age                 = Column("AGE",                  Integer)
    email               = Column("EMAIL",                String(100), unique=True, nullable=False)
    phone_number        = Column("PHONE_NUMBER",         String(20))
    gender              = Column("GENDER",               String(10))
    severity_level      = Column("SEVERITY_LEVEL",       String(50))
    reaction_symptoms   = Column("REACTION_SYMPTOMS",    String(500))
    dietary_lifestyle   = Column("DIETARY_LIFESTYLE",    String(200))
    other_diet_notes    = Column("OTHER_DIET_NOTES",     String(1000))
    risk_management     = Column("RISK_MANAGEMENT_HABIT",String(200))
    created_at          = Column("CREATED_AT",           TIMESTAMP, server_default=func.current_timestamp())

    allergies    = relationship("UserAllergy",  back_populates="user", cascade="all, delete-orphan")
    scan_history = relationship("ScanHistory",  back_populates="user", cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
#  ALLERGIES
# ─────────────────────────────────────────────────────────────────────────────
class Allergy(Base):
    __tablename__ = "ALLERGIES"

    allergy_id   = Column("ALLERGY_ID",   Integer, primary_key=True)
    allergy_type = Column("ALLERGY_TYPE", String(100), nullable=False)

    users    = relationship("UserAllergy",    back_populates="allergy")
    products = relationship("ProductAllergy", back_populates="allergy")


# ─────────────────────────────────────────────────────────────────────────────
#  USER ↔ ALLERGY (Join Table)
# ─────────────────────────────────────────────────────────────────────────────
class UserAllergy(Base):
    __tablename__ = "USER_ALLERGY"

    user_id    = Column("USER_ID",    Integer, ForeignKey("USERS.USER_ID"),    primary_key=True)
    allergy_id = Column("ALLERGY_ID", Integer, ForeignKey("ALLERGIES.ALLERGY_ID"), primary_key=True)

    user    = relationship("User",    back_populates="allergies")
    allergy = relationship("Allergy", back_populates="users")


# ─────────────────────────────────────────────────────────────────────────────
#  PRODUCTS
# ─────────────────────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "PRODUCTS"

    product_id   = Column("PRODUCT_ID",   Integer, primary_key=True)
    barcode      = Column("BARCODE",      String(50),   unique=True, index=True)
    product_name = Column("PRODUCT_NAME", String(250),  nullable=False)
    brand        = Column("BRAND",        String(100))
    category     = Column("CATEGORY",     String(100))
    ingredients  = Column("INGREDIENTS",  String(4000))

    # التوافق مع مسمى الجمع في قاعدة البيانات
    alternatives = Column("ALTERNATIVES", String(250))

    allergies    = relationship("ProductAllergy", back_populates="product")
    scan_history = relationship("ScanHistory",    back_populates="product")


# ─────────────────────────────────────────────────────────────────────────────
#  PRODUCT ↔ ALLERGY (Join Table)
# ─────────────────────────────────────────────────────────────────────────────
class ProductAllergy(Base):
    __tablename__ = "PRODUCT_ALLERGY"

    product_id = Column("PRODUCT_ID", Integer, ForeignKey("PRODUCTS.PRODUCT_ID"), primary_key=True)
    allergy_id = Column("ALLERGY_ID", Integer, ForeignKey("ALLERGIES.ALLERGY_ID"), primary_key=True)

    product = relationship("Product", back_populates="allergies")
    allergy = relationship("Allergy", back_populates="products")


# ─────────────────────────────────────────────────────────────────────────────
#  SCAN HISTORY
# ─────────────────────────────────────────────────────────────────────────────
class ScanHistory(Base):
    __tablename__ = "SCAN_HISTORY"

    scan_id     = Column("SCAN_ID",    Integer, primary_key=True)
    user_id     = Column("USER_ID",    Integer, ForeignKey("USERS.USER_ID"), nullable=False)
    product_id  = Column("PRODUCT_ID", Integer, ForeignKey("PRODUCTS.PRODUCT_ID"), nullable=True)
    barcode     = Column("BARCODE",    String(50))
    result      = Column("RESULT",     String(20))
    danger_info = Column("DANGER_INFO", String(500))
    scanned_at  = Column("SCANNED_AT", TIMESTAMP, server_default=func.current_timestamp())

    user    = relationship("User",    back_populates="scan_history")
    product = relationship("Product", back_populates="scan_history")
"""
SafeBite — Pydantic Schemas
All request bodies and response models, fully typed.
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
class SignUpRequest(BaseModel):
    username:           str
    password:           str
    full_name:          Optional[str] = None
    age:                Optional[int] = None
    email:              EmailStr
    phone_number:       Optional[str] = None
    gender:             Optional[str] = None
    allergies:          List[str]     = []
    severity_level:     Optional[str] = None
    reaction_symptoms:  Optional[str] = None
    dietary_lifestyle:  Optional[str] = None
    other_diet_notes:   Optional[str] = None
    risk_management:    Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_ok(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_ok(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class SignInRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut


# ─────────────────────────────────────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────────────────────────────────────
class AllergyOut(BaseModel):
    allergy_id:   int
    allergy_type: str
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    user_id:          int
    username:         str
    full_name:        Optional[str]
    age:              Optional[int]
    email:            str
    phone_number:     Optional[str]
    gender:             Optional[str]
    severity_level:   Optional[str]
    reaction_symptoms:Optional[str]
    dietary_lifestyle:Optional[str]
    other_diet_notes: Optional[str]
    risk_management:  Optional[str]
    created_at:       Optional[datetime]
    allergies:        List[AllergyOut] = []
    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    full_name:          Optional[str] = None
    age:                Optional[int] = None
    phone_number:       Optional[str] = None
    gender:             Optional[str] = None
    allergies:          Optional[List[str]] = None
    severity_level:     Optional[str] = None
    reaction_symptoms:  Optional[str] = None
    dietary_lifestyle:  Optional[str] = None
    other_diet_notes:   Optional[str] = None
    risk_management:    Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
#  SCANNER
# ─────────────────────────────────────────────────────────────────────────────
class ScanRequest(BaseModel):
    barcode: str


class AlternativeOut(BaseModel):
    product_id:   int
    product_name: str
    brand:        Optional[str]
    barcode:      Optional[str]
    model_config = {"from_attributes": True}


class ScanResult(BaseModel):
    barcode:      str
    product_name: Optional[str]
    brand:        Optional[str]
    ingredients:  Optional[str]
    result:       str
    danger_info:  Optional[str]
    allergens_found: List[str] = []
    alternatives:    List[AlternativeOut] = [] # تأكيد المسمى بالجمع


# ─────────────────────────────────────────────────────────────────────────────
#  SCAN HISTORY
# ─────────────────────────────────────────────────────────────────────────────
class ScanHistoryOut(BaseModel):
    scan_id:      int
    barcode:      Optional[str]
    product_name: Optional[str]
    result:       str
    danger_info:  Optional[str]
    scanned_at:   Optional[datetime]
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
#  AI ASSISTANT
# ─────────────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    status: str
    reply:  str


# ─────────────────────────────────────────────────────────────────────────────
#  GENERIC
# ─────────────────────────────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str
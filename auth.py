"""
SafeBite — Authentication Router
Handles User Registration (Signup/Get Started) and JWT-based Login (Signin).
Includes logic for linking initial health profiles and allergies to Oracle DB.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User, Allergy, UserAllergy
from schemas import SignUpRequest, SignInRequest, TokenResponse, UserOut, AllergyOut
from security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _build_user_out(user: User) -> UserOut:
    """Helper to convert User ORM objects into the UserOut Schema for frontend display."""
    allergy_list = [
        AllergyOut(allergy_id=ua.allergy.allergy_id, allergy_type=ua.allergy.allergy_type)
        for ua in user.allergies if ua.allergy
    ]
    return UserOut(
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        age=user.age,
        email=user.email,
        phone_number=user.phone_number,
        gender=user.gender,
        severity_level=user.severity_level,
        reaction_symptoms=user.reaction_symptoms,
        dietary_lifestyle=user.dietary_lifestyle,
        other_diet_notes=user.other_diet_notes,
        risk_management=user.risk_management,
        created_at=user.created_at,
        allergies=allergy_list,
    )


def _get_or_create_allergy(db: Session, allergy_name: str) -> Allergy:
    """Finds an existing allergy or creates a new entry in the ALLERGIES table."""
    allergy = db.query(Allergy).filter(Allergy.allergy_type.ilike(allergy_name.strip())).first()
    if not allergy:
        allergy = Allergy(allergy_type=allergy_name.strip())
        db.add(allergy)
        db.flush()  # الحصول على ID الحساسية قبل الحفظ النهائي
    return allergy


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(body: SignUpRequest, db: Session = Depends(get_db)):
    """
    Acts as the 'Get Started' logic.
    Registers a new user and grants immediate access via JWT token.
    """
    # 1. التأكد من عدم تكرار الإيميل أو اسم المستخدم قبل المحاولة لتجنب ORA-00001
    if db.query(User).filter((User.email == body.email) | (User.username == body.username)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or Email already registered"
        )

    try:
        # 2. إنشاء كائن المستخدم الجديد
        user = User(
            username=body.username,
            password=hash_password(body.password),
            full_name=body.full_name,
            age=body.age,
            email=str(body.email),
            phone_number=body.phone_number,
            gender=body.gender,
            severity_level=body.severity_level,
            reaction_symptoms=body.reaction_symptoms,
            dietary_lifestyle=body.dietary_lifestyle,
            other_diet_notes=body.other_diet_notes,
            risk_management=body.risk_management,
        )
        db.add(user)
        db.flush()  # لإنشاء USER_ID لاستخدامه في ربط الحساسية

        # 3. ربط الحساسية المختارة بالحساب
        if body.allergies:
            for allergy_name in body.allergies:
                if allergy_name and allergy_name.strip():
                    allergy = _get_or_create_allergy(db, allergy_name)
                    db.add(UserAllergy(user_id=user.user_id, allergy_id=allergy.allergy_id))

        db.commit()
        db.refresh(user)

        # 4. توليد التوكن فوراً ليدخل المستخدم للموقع مباشرة (تنشيط تلقائي)
        token = create_access_token({"sub": str(user.user_id)})
        return TokenResponse(access_token=token, user=_build_user_out(user))

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data integrity error. Check your inputs.")


@router.post("/signin", response_model=TokenResponse)
def signin(body: SignInRequest, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns a secure JWT access token."""
    user = db.query(User).filter(User.email == str(body.email)).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(user.user_id)})
    return TokenResponse(access_token=token, user=_build_user_out(user))
"""
Company profile API routes (P0: F50, F53).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..api.deps import get_current_user
from ..database import get_db
from ..models.company import Company
from ..models.user import User
from ..schemas.company import CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/company", tags=["Company"])


@router.get("/profile", response_model=CompanyResponse)
async def get_company_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's company profile."""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    return company


@router.put("/profile", response_model=CompanyResponse)
async def upsert_company_profile(
    payload: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update company profile for current user.

    For P0 UX, this acts as upsert: if profile does not exist, create it using
    required fields from the payload.
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()

    # Create profile if missing (P0 flow friendliness).
    if not company:
        required_fields = ["gstin", "legal_name", "address", "state_code", "turnover_slab"]
        missing = [name for name in required_fields if not getattr(payload, name, None)]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields for company profile: {', '.join(missing)}",
            )

        company = Company(
            user_id=current_user.id,
            gstin=payload.gstin,
            legal_name=payload.legal_name,
            trade_name=payload.trade_name,
            address=payload.address,
            state_code=payload.state_code,
            turnover_slab=payload.turnover_slab,
            filing_frequency=payload.filing_frequency or "monthly",
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    # Update existing profile.
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company

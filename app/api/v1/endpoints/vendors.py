from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
# from app.schemas.vendor import Vendor, VendorCreate, VendorUpdate
# from app.schemas.user import UserOut

router = APIRouter()

@router.get("/", response_model=List[dict])
def list_vendors(db: Session = Depends(deps.get_db)):
    """List all vendors (placeholder)."""
    return []

@router.post("/", response_model=dict)
def create_vendor(db: Session = Depends(deps.get_db)):
    """Add a new vendor (placeholder)."""
    return {"msg": "Vendor created"}

@router.get("/{vendor_id}", response_model=dict)
def get_vendor(vendor_id: int, db: Session = Depends(deps.get_db)):
    """Get vendor details (placeholder)."""
    return {"id": vendor_id}

@router.put("/{vendor_id}", response_model=dict)
def update_vendor(vendor_id: int, db: Session = Depends(deps.get_db)):
    """Update vendor details (placeholder)."""
    return {"msg": "Vendor updated"}

@router.delete("/{vendor_id}", response_model=dict)
def delete_vendor(vendor_id: int, db: Session = Depends(deps.get_db)):
    """Delete vendor (placeholder)."""
    return {"msg": "Vendor deleted"}

@router.post("/{vendor_id}/nda", response_model=dict)
def upload_nda(vendor_id: int, db: Session = Depends(deps.get_db)):
    """Upload NDA/contract (placeholder)."""
    return {"msg": "NDA uploaded"}

@router.get("/{vendor_id}/timeline", response_model=dict)
def get_timeline(vendor_id: int, db: Session = Depends(deps.get_db)):
    """Get vendor communication timeline (placeholder)."""
    return {"msg": "Timeline"}

@router.post("/{vendor_id}/acknowledge", response_model=dict)
def acknowledge_spec(vendor_id: int, db: Session = Depends(deps.get_db)):
    """Acknowledge spec (placeholder)."""
    return {"msg": "Spec acknowledged"} 
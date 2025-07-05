from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# from app.schemas.api_key import ApiKey, ApiKeyCreate
from app.api import deps

router = APIRouter()

@router.get("/", response_model=dict)
def list_api_keys(db: Session = Depends(deps.get_db)):
    """List API keys (placeholder)."""
    return {"msg": "List of API keys"}

@router.post("/", response_model=dict)
def create_api_key(db: Session = Depends(deps.get_db)):
    """Generate new API key (placeholder)."""
    return {"msg": "API key created"}

@router.post("/{key_id}/regenerate", response_model=dict)
def regenerate_api_key(key_id: int, db: Session = Depends(deps.get_db)):
    """Regenerate API key (placeholder)."""
    return {"msg": "API key regenerated"}

@router.delete("/{key_id}", response_model=dict)
def delete_api_key(key_id: int, db: Session = Depends(deps.get_db)):
    """Delete API key (placeholder)."""
    return {"msg": "API key deleted"} 
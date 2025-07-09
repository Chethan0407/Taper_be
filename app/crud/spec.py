from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime

from app.core.config import settings
from app.db.models import Spec, Project, Company
from app.schemas.spec import SpecCreate, SpecUpdate

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def get_spec(db: Session, spec_id: int) -> Optional[Spec]:
    return db.query(Spec).filter(Spec.id == spec_id).first()

def get_specs(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Spec]:
    return db.query(Spec)\
        .filter(Spec.project_id == project_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

async def create_spec(
    db: Session,
    spec_in: SpecCreate,
    file: UploadFile,
    author_id: int
) -> Spec:
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == spec_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Generate S3 key
    file_extension = os.path.splitext(file.filename)[1]
    s3_key = f"specs/{project.id}/{spec_in.version}/{file.filename}"
    
    try:
        # Upload to S3
        file_content = await file.read()
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=s3_key,
            Body=file_content
        )
        
        # Create spec record
        db_spec = Spec(
            **{k: v for k, v in spec_in.dict().items() if k != 'metadata'},
            spec_metadata=spec_in.spec_metadata,
            file_path=s3_key,
            author_id=author_id
        )
        db.add(db_spec)
        db.commit()
        db.refresh(db_spec)
        return db_spec
        
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

def update_spec(
    db: Session,
    spec_id: int,
    spec_in: SpecUpdate,
    company_owner_id: int
) -> Optional[Spec]:
    db_spec = get_spec(db, spec_id)
    if not db_spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found"
        )
    
    # Verify user owns the company
    project = db.query(Project).filter(Project.id == db_spec.project_id).first()
    company = db.query(Company).filter(Company.id == project.company_id).first()
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in spec_in.dict(exclude_unset=True).items():
        setattr(db_spec, field, value)
    
    db_spec.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_spec)
    return db_spec

def delete_spec(
    db: Session,
    spec_id: int,
    company_owner_id: int
) -> bool:
    db_spec = get_spec(db, spec_id)
    if not db_spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found"
        )
    
    # Verify user owns the company
    project = db.query(Project).filter(Project.id == db_spec.project_id).first()
    company = db.query(Company).filter(Company.id == project.company_id).first()
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        # Delete from S3
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=db_spec.file_path
        )
        
        # Delete from database
        db.delete(db_spec)
        db.commit()
        return True
        
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        ) 

def generate_presigned_url(file_path: str, expires_in: int = 60 * 60 * 3) -> str:
    """
    Generate a presigned URL for the given S3 file path, valid for a few hours (default: 3 hours).
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET, 'Key': file_path},
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        # Optionally log the error
        return None 
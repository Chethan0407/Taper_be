import os
import logging
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import ActiveChecklistItem
from app.core.logging import get_logger

logger = get_logger(__name__)

def sync_files_and_db():
    """Sync files on disk with database entries on startup."""
    try:
        # Get database session
        db = next(get_db())
        
        # Scan evidence files directory
        evidence_dir = "uploads/checklist_evidence"
        if not os.path.exists(evidence_dir):
            os.makedirs(evidence_dir, exist_ok=True)
            logger.info("Created evidence directory", path=evidence_dir)
            return
        
        # Get all files in evidence directory
        files_on_disk = set()
        for filename in os.listdir(evidence_dir):
            file_path = os.path.join(evidence_dir, filename)
            if os.path.isfile(file_path):
                files_on_disk.add(file_path)
        
        # Get all file paths from database
        db_items = db.query(ActiveChecklistItem).filter(
            ActiveChecklistItem.evidence_file_path.isnot(None)
        ).all()
        files_in_db = {item.evidence_file_path for item in db_items if item.evidence_file_path}
        
        # Find orphaned files (on disk but not in DB)
        orphaned_files = files_on_disk - files_in_db
        if orphaned_files:
            logger.warning(
                "Found orphaned evidence files",
                count=len(orphaned_files),
                files=list(orphaned_files)
            )
        
        # Find missing files (in DB but not on disk)
        missing_files = files_in_db - files_on_disk
        if missing_files:
            logger.warning(
                "Found missing evidence files",
                count=len(missing_files),
                files=list(missing_files)
            )
        
        # Log summary
        logger.info(
            "File sync completed",
            total_files_on_disk=len(files_on_disk),
            total_files_in_db=len(files_in_db),
            orphaned_files=len(orphaned_files),
            missing_files=len(missing_files)
        )
        
    except Exception as e:
        logger.error("File sync failed", error=str(e))
    finally:
        db.close()

def cleanup_orphaned_files():
    """Optional: Clean up orphaned files (use with caution)."""
    try:
        evidence_dir = "uploads/checklist_evidence"
        if not os.path.exists(evidence_dir):
            return
        
        db = next(get_db())
        
        # Get all file paths from database
        db_items = db.query(ActiveChecklistItem).filter(
            ActiveChecklistItem.evidence_file_path.isnot(None)
        ).all()
        files_in_db = {item.evidence_file_path for item in db_items if item.evidence_file_path}
        
        # Find and remove orphaned files
        orphaned_count = 0
        for filename in os.listdir(evidence_dir):
            file_path = os.path.join(evidence_dir, filename)
            if os.path.isfile(file_path) and file_path not in files_in_db:
                os.remove(file_path)
                orphaned_count += 1
        
        if orphaned_count > 0:
            logger.info("Cleaned up orphaned files", count=orphaned_count)
        
    except Exception as e:
        logger.error("Cleanup failed", error=str(e))
    finally:
        db.close() 
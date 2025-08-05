"""
Content management router for Vaani Sentinel X
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import csv
import io
import uuid
from datetime import datetime

from core.database import get_db, DatabaseManager
from api.models import (
    ContentInput, ContentUpload, ContentResponse, 
    StatusResponse, ErrorResponse
)
from api.routers.auth import get_current_user
from agents.miner_sanitizer import KnowledgeMinerSanitizer

router = APIRouter()

@router.post("/upload-csv", response_model=StatusResponse)
async def upload_csv_content(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process CSV content"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        # Read CSV content
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        # Save temporary file
        temp_filename = f"temp_{uuid.uuid4()}.csv"
        temp_path = f"./temp/{temp_filename}"
        
        import os
        os.makedirs("./temp", exist_ok=True)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Process with Agent A
        miner = KnowledgeMinerSanitizer()
        content_blocks = miner.process_csv_input(temp_path)
        
        # Save to database
        saved_content = []
        for block_data in miner.get_structured_content():
            content_data = {
                "content_id": block_data["content_id"],
                "original_text": block_data["text"],
                "language": "en",  # Default, can be detected
                "content_type": "raw",
                "content_metadata": block_data["metadata"],
                "is_verified": block_data["verification_score"] >= 70.0,
                "verification_score": block_data["verification_score"]
            }
            
            content = DatabaseManager.create_content(db, content_data)
            saved_content.append(content.content_id)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return StatusResponse(
            status="success",
            message=f"Processed {len(content_blocks)} content blocks from CSV",
            timestamp=datetime.utcnow(),
            data={
                "processed_count": len(content_blocks),
                "verified_count": len([b for b in content_blocks if b.verification_score >= 70.0]),
                "content_ids": saved_content
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV: {str(e)}"
        )

@router.post("/upload-json", response_model=StatusResponse)
async def upload_json_content(
    content_upload: ContentUpload,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process JSON content"""
    try:
        # Process with Agent A
        miner = KnowledgeMinerSanitizer()
        content_blocks = miner.process_json_input(content_upload.data)
        
        # Save to database
        saved_content = []
        for block_data in miner.get_structured_content():
            content_data = {
                "content_id": block_data["content_id"],
                "original_text": block_data["text"],
                "language": "en",  # Default, can be detected
                "content_type": "raw",
                "content_metadata": block_data["metadata"],
                "is_verified": block_data["verification_score"] >= 70.0,
                "verification_score": block_data["verification_score"]
            }
            
            content = DatabaseManager.create_content(db, content_data)
            saved_content.append(content.content_id)
        
        return StatusResponse(
            status="success",
            message=f"Processed {len(content_blocks)} content blocks from JSON",
            timestamp=datetime.utcnow(),
            data={
                "processed_count": len(content_blocks),
                "verified_count": len([b for b in content_blocks if b.verification_score >= 70.0]),
                "content_ids": saved_content
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing JSON: {str(e)}"
        )

@router.post("/create", response_model=ContentResponse)
async def create_content(
    content_input: ContentInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create single content item"""
    try:
        # Process with Agent A
        miner = KnowledgeMinerSanitizer()
        content_blocks = miner.process_json_input([{"text": content_input.text}])
        
        if not content_blocks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process content"
            )
        
        block_data = miner.get_structured_content()[0]
        
        # Save to database
        content_data = {
            "content_id": block_data["content_id"],
            "original_text": block_data["text"],
            "language": content_input.language,
            "content_type": content_input.content_type.value,
            "content_metadata": {**block_data["metadata"], **content_input.metadata},
            "is_verified": block_data["verification_score"] >= 70.0,
            "verification_score": block_data["verification_score"]
        }
        
        content = DatabaseManager.create_content(db, content_data)
        
        return ContentResponse(
            content_id=content.content_id,
            original_text=content.original_text,
            language=content.language,
            content_type=content.content_type,
            metadata=content.content_metadata or {},
            created_at=content.created_at,
            is_verified=content.is_verified,
            verification_score=content.verification_score
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating content: {str(e)}"
        )

@router.get("/list", response_model=List[ContentResponse])
async def list_content(
    skip: int = 0,
    limit: int = 100,
    verified_only: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List content items"""
    try:
        from core.database import Content
        
        query = db.query(Content)
        
        if verified_only:
            query = query.filter(Content.is_verified == True)
        
        contents = query.offset(skip).limit(limit).all()
        
        return [
            ContentResponse(
                content_id=content.content_id,
                original_text=content.original_text,
                language=content.language,
                content_type=content.content_type,
                metadata=content.content_metadata or {},
                created_at=content.created_at,
                is_verified=content.is_verified,
                verification_score=content.verification_score
            )
            for content in contents
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing content: {str(e)}"
        )

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific content item"""
    try:
        content = DatabaseManager.get_content_by_id(db, content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        return ContentResponse(
            content_id=content.content_id,
            original_text=content.original_text,
            language=content.language,
            content_type=content.content_type,
            metadata=content.content_metadata or {},
            created_at=content.created_at,
            is_verified=content.is_verified,
            verification_score=content.verification_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content: {str(e)}"
        )

@router.delete("/{content_id}", response_model=StatusResponse)
async def delete_content(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete content item"""
    try:
        from core.database import Content
        
        content = db.query(Content).filter(Content.content_id == content_id).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        db.delete(content)
        db.commit()
        
        return StatusResponse(
            status="success",
            message="Content deleted successfully",
            timestamp=datetime.utcnow(),
            data={"content_id": content_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting content: {str(e)}"
        )

"""
Security router for Vaani Sentinel X
Exposes security and ethics guard functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from core.database import get_db, DatabaseManager
from api.models import StatusResponse, SecurityFlagResponse
from api.routers.auth import get_current_user
from agents.security_guard import SecurityGuard, FlagType, Severity

router = APIRouter()

# Request Models
class SecurityAnalysisRequest(BaseModel):
    content_id: str

class EncryptionRequest(BaseModel):
    content: str
    language: str = "en"

class KillSwitchRequest(BaseModel):
    reason: str

class ArchiveRequest(BaseModel):
    content_ids: List[str]
    language: str

# Response Models
class SecurityAnalysisResponse(BaseModel):
    content_id: str
    flags_count: int
    flags: List[Dict[str, Any]]
    risk_level: str
    recommendations: List[str]

class EncryptionResponse(BaseModel):
    encrypted_data: str
    checksum: str
    content_id: str

class DashboardResponse(BaseModel):
    kill_switch_active: bool
    flag_statistics: Dict[str, Any]
    system_status: str
    last_updated: str

@router.post("/analyze-content", response_model=SecurityAnalysisResponse)
async def analyze_content_security(
    request: SecurityAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze content for security issues"""
    try:
        # Get content
        content = DatabaseManager.get_content_by_id(db, request.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Initialize security guard
        security_guard = SecurityGuard()
        
        # Analyze content
        flags = security_guard.analyze_content_security(
            content.original_text, 
            request.content_id
        )
        
        # Determine risk level
        risk_level = "low"
        if any(flag.severity.value in ["high", "critical"] for flag in flags):
            risk_level = "high"
        elif any(flag.severity.value == "medium" for flag in flags):
            risk_level = "medium"
        
        # Generate recommendations
        recommendations = []
        flag_types = [flag.flag_type.value for flag in flags]
        
        if "hate_speech" in flag_types:
            recommendations.append("Content contains hate speech - immediate review required")
        if "religious_bias" in flag_types or "political_bias" in flag_types:
            recommendations.append("Content shows bias - consider neutral rephrasing")
        if "profanity" in flag_types:
            recommendations.append("Remove profane language before publishing")
        if "misinformation" in flag_types:
            recommendations.append("Verify facts and add credible sources")
        
        # Convert flags to response format
        flag_data = [
            {
                "flag_id": flag.flag_id,
                "type": flag.flag_type.value,
                "severity": flag.severity.value,
                "details": flag.details,
                "created_at": flag.created_at.isoformat()
            }
            for flag in flags
        ]
        
        return SecurityAnalysisResponse(
            content_id=request.content_id,
            flags_count=len(flags),
            flags=flag_data,
            risk_level=risk_level,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing content security: {str(e)}"
        )

@router.post("/encrypt-content", response_model=EncryptionResponse)
async def encrypt_content(
    request: EncryptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Encrypt content"""
    try:
        security_guard = SecurityGuard()
        
        encrypted_data, checksum = security_guard.encrypt_content(
            request.content,
            request.language
        )
        
        return EncryptionResponse(
            encrypted_data=encrypted_data,
            checksum=checksum,
            content_id=f"encrypted_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error encrypting content: {str(e)}"
        )

@router.post("/decrypt-content")
async def decrypt_content(
    encrypted_data: str,
    checksum: str,
    current_user: dict = Depends(get_current_user)
):
    """Decrypt content"""
    try:
        security_guard = SecurityGuard()
        
        decrypted_data = security_guard.decrypt_content(encrypted_data, checksum)
        
        return {
            "status": "success",
            "decrypted_data": decrypted_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error decrypting content: {str(e)}"
        )

@router.post("/create-archive", response_model=StatusResponse)
async def create_encrypted_archive(
    request: ArchiveRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create encrypted archive for content"""
    try:
        # Get content items
        contents = []
        for content_id in request.content_ids:
            content = DatabaseManager.get_content_by_id(db, content_id)
            if content:
                contents.append({
                    "content_id": content.content_id,
                    "text": content.original_text,
                    "language": content.language,
                    "metadata": content.content_metadata
                })
        
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid content found"
            )
        
        # Create encrypted archive
        security_guard = SecurityGuard()
        archive_path = security_guard.create_encrypted_archive(contents, request.language)
        
        return StatusResponse(
            status="success",
            message=f"Encrypted archive created for {len(contents)} content items",
            timestamp=datetime.utcnow(),
            data={
                "archive_path": archive_path,
                "content_count": len(contents),
                "language": request.language
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating archive: {str(e)}"
        )

@router.post("/kill-switch/activate", response_model=StatusResponse)
async def activate_kill_switch(
    request: KillSwitchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Activate kill switch"""
    try:
        security_guard = SecurityGuard()
        success = security_guard.activate_kill_switch(request.reason)
        
        if success:
            return StatusResponse(
                status="success",
                message="Kill switch activated - all operations blocked",
                timestamp=datetime.utcnow(),
                data={"reason": request.reason}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate kill switch"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating kill switch: {str(e)}"
        )

@router.post("/kill-switch/deactivate", response_model=StatusResponse)
async def deactivate_kill_switch(
    current_user: dict = Depends(get_current_user)
):
    """Deactivate kill switch"""
    try:
        security_guard = SecurityGuard()
        success = security_guard.deactivate_kill_switch()
        
        if success:
            return StatusResponse(
                status="success",
                message="Kill switch deactivated - operations resumed",
                timestamp=datetime.utcnow()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate kill switch"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating kill switch: {str(e)}"
        )

@router.get("/kill-switch/status")
async def get_kill_switch_status(
    current_user: dict = Depends(get_current_user)
):
    """Get kill switch status"""
    try:
        security_guard = SecurityGuard()
        
        return {
            "kill_switch_active": security_guard.kill_switch_active,
            "status": "blocked" if security_guard.kill_switch_active else "active",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking kill switch status: {str(e)}"
        )

@router.get("/dashboard", response_model=DashboardResponse)
async def get_security_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get security dashboard data"""
    try:
        security_guard = SecurityGuard()
        dashboard_data = security_guard.get_security_dashboard_data()
        
        return DashboardResponse(
            kill_switch_active=dashboard_data["kill_switch_active"],
            flag_statistics=dashboard_data["flag_statistics"],
            system_status=dashboard_data["system_status"],
            last_updated=dashboard_data["last_updated"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )

@router.get("/flags/recent")
async def get_recent_security_flags(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get recent security flags"""
    try:
        security_guard = SecurityGuard()
        dashboard_data = security_guard.get_security_dashboard_data()
        
        recent_flags = dashboard_data["flag_statistics"]["recent_flags"]
        
        return {
            "flags": recent_flags[:limit],
            "total_count": len(recent_flags),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recent flags: {str(e)}"
        )

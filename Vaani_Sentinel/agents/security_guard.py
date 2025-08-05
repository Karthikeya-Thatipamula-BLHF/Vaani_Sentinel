"""
Agent E: Security & Ethics Guard
Implements security layer with content flagging, encryption, and monitoring
"""

import re
import os
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from enum import Enum

class FlagType(Enum):
    PROFANITY = "profanity"
    BIAS = "bias"
    CONTROVERSY = "controversy"
    RELIGIOUS_BIAS = "religious_bias"
    POLITICAL_BIAS = "political_bias"
    HATE_SPEECH = "hate_speech"
    MISINFORMATION = "misinformation"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityFlag:
    def __init__(self, flag_type: FlagType, severity: Severity, details: Dict[str, Any]):
        self.flag_id = str(uuid.uuid4())
        self.flag_type = flag_type
        self.severity = severity
        self.details = details
        self.created_at = datetime.utcnow()

class SecurityGuard:
    """Agent E: Security & Ethics Guard"""
    
    def __init__(self):
        self.security_logs_path = "./logs/security"
        self.archives_path = "./archives"
        self.kill_switch_path = "./kill_switch.json"
        
        # Create directories
        os.makedirs(self.security_logs_path, exist_ok=True)
        os.makedirs(self.archives_path, exist_ok=True)
        
        # Initialize encryption
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security patterns and keywords
        self._initialize_security_patterns()
        
        # Kill switch status
        self.kill_switch_active = self._check_kill_switch()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = "./config/encryption.key"
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _initialize_security_patterns(self):
        """Initialize security detection patterns"""
        
        # Profanity patterns (basic examples)
        self.profanity_patterns = [
            r'\b(damn|hell|crap)\b',
            r'\b(stupid|idiot|moron)\b'
        ]
        
        # Religious bias keywords
        self.religious_bias_keywords = [
            "infidel", "heretic", "blasphemy", "false prophet",
            "religious war", "holy war", "crusade", "jihad"
        ]
        
        # Political bias keywords
        self.political_bias_keywords = [
            "radical left", "radical right", "fascist", "communist",
            "liberal agenda", "conservative agenda", "deep state"
        ]
        
        # Controversy keywords
        self.controversy_keywords = [
            "controversial", "disputed", "debated", "contentious",
            "polarizing", "divisive", "inflammatory"
        ]
        
        # Hate speech patterns
        self.hate_speech_patterns = [
            r'\b(hate|despise|loathe)\s+(all|every)\s+\w+',
            r'\b(kill|destroy|eliminate)\s+(all|every)\s+\w+'
        ]
        
        # Misinformation indicators
        self.misinformation_indicators = [
            "proven fact", "scientists agree", "studies show",
            "everyone knows", "obvious truth", "undeniable"
        ]
    
    def analyze_content_security(self, content: str, content_id: str) -> List[SecurityFlag]:
        """Analyze content for security issues"""
        
        if self.kill_switch_active:
            raise Exception("Kill switch is active - content analysis blocked")
        
        flags = []
        content_lower = content.lower()
        
        # Check profanity
        profanity_flags = self._check_profanity(content, content_lower)
        flags.extend(profanity_flags)
        
        # Check religious bias
        religious_flags = self._check_religious_bias(content, content_lower)
        flags.extend(religious_flags)
        
        # Check political bias
        political_flags = self._check_political_bias(content, content_lower)
        flags.extend(political_flags)
        
        # Check controversy
        controversy_flags = self._check_controversy(content, content_lower)
        flags.extend(controversy_flags)
        
        # Check hate speech
        hate_flags = self._check_hate_speech(content, content_lower)
        flags.extend(hate_flags)
        
        # Check misinformation
        misinfo_flags = self._check_misinformation(content, content_lower)
        flags.extend(misinfo_flags)
        
        # Log security analysis
        self._log_security_analysis(content_id, content, flags)
        
        return flags
    
    def _check_profanity(self, content: str, content_lower: str) -> List[SecurityFlag]:
        """Check for profanity"""
        flags = []
        
        for pattern in self.profanity_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                flags.append(SecurityFlag(
                    flag_type=FlagType.PROFANITY,
                    severity=Severity.MEDIUM,
                    details={
                        "matches": matches,
                        "pattern": pattern,
                        "count": len(matches)
                    }
                ))
        
        return flags
    
    def _check_religious_bias(self, content: str, content_lower: str) -> List[SecurityFlag]:
        """Check for religious bias"""
        flags = []
        matches = []
        
        for keyword in self.religious_bias_keywords:
            if keyword.lower() in content_lower:
                matches.append(keyword)
        
        if matches:
            severity = Severity.HIGH if len(matches) > 2 else Severity.MEDIUM
            flags.append(SecurityFlag(
                flag_type=FlagType.RELIGIOUS_BIAS,
                severity=severity,
                details={
                    "keywords": matches,
                    "count": len(matches)
                }
            ))
        
        return flags
    
    def _check_political_bias(self, content: str, content_lower: str) -> List[SecurityFlag]:
        """Check for political bias"""
        flags = []
        matches = []
        
        for keyword in self.political_bias_keywords:
            if keyword.lower() in content_lower:
                matches.append(keyword)
        
        if matches:
            severity = Severity.HIGH if len(matches) > 2 else Severity.MEDIUM
            flags.append(SecurityFlag(
                flag_type=FlagType.POLITICAL_BIAS,
                severity=severity,
                details={
                    "keywords": matches,
                    "count": len(matches)
                }
            ))
        
        return flags
    
    def _check_controversy(self, content: str, content_lower: str) -> List[SecurityFlag]:
        """Check for controversial content"""
        flags = []
        matches = []
        
        for keyword in self.controversy_keywords:
            if keyword.lower() in content_lower:
                matches.append(keyword)
        
        if matches:
            flags.append(SecurityFlag(
                flag_type=FlagType.CONTROVERSY,
                severity=Severity.LOW,
                details={
                    "keywords": matches,
                    "count": len(matches)
                }
            ))
        
        return flags
    
    def _check_hate_speech(self, content: str, content_lower: str) -> List[SecurityFlag]:
        """Check for hate speech"""
        flags = []
        
        for pattern in self.hate_speech_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                flags.append(SecurityFlag(
                    flag_type=FlagType.HATE_SPEECH,
                    severity=Severity.CRITICAL,
                    details={
                        "matches": matches,
                        "pattern": pattern,
                        "count": len(matches)
                    }
                ))
        
        return flags
    
    def _check_misinformation(self, content: str, content_lower: str) -> List[SecurityFlag]:
        """Check for potential misinformation"""
        flags = []
        matches = []
        
        for indicator in self.misinformation_indicators:
            if indicator.lower() in content_lower:
                matches.append(indicator)
        
        if matches:
            flags.append(SecurityFlag(
                flag_type=FlagType.MISINFORMATION,
                severity=Severity.MEDIUM,
                details={
                    "indicators": matches,
                    "count": len(matches)
                }
            ))
        
        return flags
    
    def encrypt_content(self, content: str, language: str = "en") -> Tuple[str, str]:
        """Encrypt content and return encrypted data with checksum"""
        
        # Create content with metadata
        content_data = {
            "content": content,
            "language": language,
            "encrypted_at": datetime.utcnow().isoformat(),
            "content_id": str(uuid.uuid4())
        }
        
        # Convert to JSON and encrypt
        json_data = json.dumps(content_data, ensure_ascii=False)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode('utf-8'))
        
        # Generate checksum
        checksum = hashlib.sha256(encrypted_data).hexdigest()
        
        return base64.b64encode(encrypted_data).decode('utf-8'), checksum
    
    def decrypt_content(self, encrypted_data: str, checksum: str) -> Dict[str, Any]:
        """Decrypt content and verify checksum"""
        
        # Decode and verify checksum
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        calculated_checksum = hashlib.sha256(encrypted_bytes).hexdigest()
        
        if calculated_checksum != checksum:
            raise Exception("Checksum verification failed - data may be corrupted")
        
        # Decrypt
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        content_data = json.loads(decrypted_data.decode('utf-8'))
        
        return content_data
    
    def create_encrypted_archive(self, contents: List[Dict[str, Any]], language: str) -> str:
        """Create encrypted archive for specific language"""
        
        archive_dir = os.path.join(self.archives_path, f"encrypted_{language}")
        os.makedirs(archive_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"archive_{language}_{timestamp}.enc"
        archive_path = os.path.join(archive_dir, archive_filename)
        
        # Encrypt each content item
        encrypted_contents = []
        for content_item in contents:
            encrypted_data, checksum = self.encrypt_content(
                json.dumps(content_item, ensure_ascii=False),
                language
            )
            encrypted_contents.append({
                "encrypted_data": encrypted_data,
                "checksum": checksum,
                "original_id": content_item.get("content_id", "unknown")
            })
        
        # Save encrypted archive
        archive_data = {
            "language": language,
            "created_at": datetime.utcnow().isoformat(),
            "content_count": len(encrypted_contents),
            "contents": encrypted_contents
        }
        
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
        return archive_path
    
    def activate_kill_switch(self, reason: str) -> bool:
        """Activate kill switch to stop all operations"""
        
        kill_switch_data = {
            "active": True,
            "activated_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "activated_by": "security_guard"
        }
        
        with open(self.kill_switch_path, 'w', encoding='utf-8') as f:
            json.dump(kill_switch_data, f, indent=2)
        
        self.kill_switch_active = True
        
        # Log critical security event
        self._log_security_event("KILL_SWITCH_ACTIVATED", {
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return True
    
    def deactivate_kill_switch(self) -> bool:
        """Deactivate kill switch"""
        
        if os.path.exists(self.kill_switch_path):
            os.remove(self.kill_switch_path)
        
        self.kill_switch_active = False
        
        # Log security event
        self._log_security_event("KILL_SWITCH_DEACTIVATED", {
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return True
    
    def _check_kill_switch(self) -> bool:
        """Check if kill switch is active"""
        if os.path.exists(self.kill_switch_path):
            try:
                with open(self.kill_switch_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get("active", False)
            except Exception:
                return False
        return False
    
    def _log_security_analysis(self, content_id: str, content: str, flags: List[SecurityFlag]):
        """Log security analysis results"""
        
        log_data = {
            "content_id": content_id,
            "analyzed_at": datetime.utcnow().isoformat(),
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "flags_count": len(flags),
            "flags": [
                {
                    "flag_id": flag.flag_id,
                    "type": flag.flag_type.value,
                    "severity": flag.severity.value,
                    "details": flag.details,
                    "created_at": flag.created_at.isoformat()
                }
                for flag in flags
            ]
        }
        
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        log_filename = f"security_analysis_{timestamp}.json"
        log_path = os.path.join(self.security_logs_path, log_filename)
        
        # Append to daily log file
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_data)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        
        event_data = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        log_filename = f"security_events_{timestamp}.json"
        log_path = os.path.join(self.security_logs_path, log_filename)
        
        # Append to daily log file
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                events = json.load(f)
        else:
            events = []
        
        events.append(event_data)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        
        # Count flags by type and severity
        flag_stats = {
            "total_flags": 0,
            "by_type": {},
            "by_severity": {},
            "recent_flags": []
        }
        
        # Read recent security logs
        today = datetime.utcnow().strftime("%Y%m%d")
        log_path = os.path.join(self.security_logs_path, f"security_analysis_{today}.json")
        
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            for log_entry in logs[-10:]:  # Last 10 entries
                for flag in log_entry.get("flags", []):
                    flag_stats["total_flags"] += 1
                    
                    flag_type = flag["type"]
                    flag_severity = flag["severity"]
                    
                    flag_stats["by_type"][flag_type] = flag_stats["by_type"].get(flag_type, 0) + 1
                    flag_stats["by_severity"][flag_severity] = flag_stats["by_severity"].get(flag_severity, 0) + 1
                    
                    flag_stats["recent_flags"].append({
                        "content_id": log_entry["content_id"],
                        "type": flag_type,
                        "severity": flag_severity,
                        "timestamp": flag["created_at"]
                    })
        
        return {
            "kill_switch_active": self.kill_switch_active,
            "flag_statistics": flag_stats,
            "system_status": "active" if not self.kill_switch_active else "blocked",
            "last_updated": datetime.utcnow().isoformat()
        }

# Global security guard instance
security_guard = SecurityGuard()

def get_security_guard() -> SecurityGuard:
    """Get the global security guard instance"""
    return security_guard

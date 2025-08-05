"""
Agent A: Knowledge Miner & Sanitizer
Accepts raw CSV/JSON data, structures content blocks, and implements verification
"""

import csv
import json
import uuid
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from better_profanity import profanity
from textblob import TextBlob
import re
from core.config import settings

class ContentBlock:
    """Structured content block"""
    def __init__(self, content_id: str, text: str, source: str, metadata: Dict[str, Any] = None):
        self.content_id = content_id
        self.text = text
        self.source = source
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.verification_score = 0.0
        self.flags = []

class KnowledgeMinerSanitizer:
    """Agent A: Knowledge Miner & Sanitizer"""
    
    def __init__(self):
        self.profanity_enabled = settings.profanity_check_enabled
        self.bias_detection_enabled = settings.bias_detection_enabled
        self.truth_source_path = "./data/truth-source.csv"
        self.content_blocks = []
        
        # Initialize profanity filter
        profanity.load_censor_words()
        
        # Load truth source if exists
        self.truth_source = self._load_truth_source()
        
        # Bias detection keywords
        self.bias_keywords = {
            "political": ["politics", "government", "election", "vote", "party", "liberal", "conservative"],
            "religious": ["religion", "god", "allah", "jesus", "hindu", "muslim", "christian", "temple", "mosque", "church"],
            "controversial": ["controversial", "debate", "argument", "conflict", "dispute"]
        }
    
    def _load_truth_source(self) -> List[Dict[str, Any]]:
        """Load truth source data"""
        if os.path.exists(self.truth_source_path):
            try:
                truth_data = []
                with open(self.truth_source_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        truth_data.append(dict(row))
                return truth_data
            except Exception as e:
                print(f"Error loading truth source: {e}")
                return []
        return []
    
    def process_csv_input(self, file_path: str) -> List[ContentBlock]:
        """Process CSV input file"""
        try:
            content_blocks = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row_index, row in enumerate(csv_reader):
                    content_id = str(uuid.uuid4())
                    text = str(row.get('text', row.get('content', '')))
                    source = f"csv:{file_path}"
                    metadata = {
                        "row_index": row_index,
                        "original_data": dict(row)
                    }
                    
                    block = ContentBlock(content_id, text, source, metadata)
                    self._verify_content(block)
                    content_blocks.append(block)
            
            self.content_blocks.extend(content_blocks)
            return content_blocks
            
        except Exception as e:
            raise Exception(f"Error processing CSV: {e}")
    
    def process_json_input(self, data: List[Dict[str, Any]]) -> List[ContentBlock]:
        """Process JSON input data"""
        try:
            content_blocks = []
            
            for i, item in enumerate(data):
                content_id = str(uuid.uuid4())
                text = str(item.get('text', item.get('content', '')))
                source = "json:api"
                metadata = {
                    "index": i,
                    "original_data": item
                }
                
                block = ContentBlock(content_id, text, source, metadata)
                self._verify_content(block)
                content_blocks.append(block)
            
            self.content_blocks.extend(content_blocks)
            return content_blocks
            
        except Exception as e:
            raise Exception(f"Error processing JSON: {e}")
    
    def _verify_content(self, block: ContentBlock):
        """Verify content block"""
        score = 100.0  # Start with perfect score
        
        # Profanity check
        if self.profanity_enabled:
            profanity_score = self._check_profanity(block.text)
            score -= profanity_score
            if profanity_score > 0:
                block.flags.append(f"profanity_detected:{profanity_score}")
        
        # Bias detection
        if self.bias_detection_enabled:
            bias_score = self._detect_bias(block.text)
            score -= bias_score
            if bias_score > 0:
                block.flags.append(f"bias_detected:{bias_score}")
        
        # Truth source validation
        truth_score = self._validate_against_truth_source(block.text)
        score += truth_score  # Add points for truth alignment
        if truth_score < 0:
            block.flags.append(f"truth_mismatch:{abs(truth_score)}")
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(block.text)
        block.metadata['sentiment'] = sentiment
        
        block.verification_score = max(0.0, min(100.0, score))
    
    def _check_profanity(self, text: str) -> float:
        """Check for profanity in text"""
        if profanity.contains_profanity(text):
            # Count profane words
            words = text.lower().split()
            profane_count = sum(1 for word in words if profanity.contains_profanity(word))
            return min(50.0, profane_count * 10.0)  # Max 50 points deduction
        return 0.0
    
    def _detect_bias(self, text: str) -> float:
        """Detect bias in text"""
        text_lower = text.lower()
        bias_score = 0.0
        
        for bias_type, keywords in self.bias_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                bias_score += matches * 5.0  # 5 points per biased keyword
                
        return min(30.0, bias_score)  # Max 30 points deduction
    
    def _validate_against_truth_source(self, text: str) -> float:
        """Validate against truth source"""
        if not self.truth_source:
            return 0.0
        
        # Simple keyword matching (can be enhanced with semantic similarity)
        text_lower = text.lower()
        matches = 0
        
        for truth_item in self.truth_source:
            truth_text = str(truth_item.get('text', '')).lower()
            if truth_text and truth_text in text_lower:
                matches += 1
        
        if matches > 0:
            return 10.0  # Bonus points for truth alignment
        return 0.0
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,  # -1 to 1
            "subjectivity": blob.sentiment.subjectivity  # 0 to 1
        }
    
    def get_structured_content(self) -> List[Dict[str, Any]]:
        """Get all structured content blocks"""
        return [
            {
                "content_id": block.content_id,
                "text": block.text,
                "source": block.source,
                "metadata": block.metadata,
                "created_at": block.created_at.isoformat(),
                "verification_score": block.verification_score,
                "flags": block.flags
            }
            for block in self.content_blocks
        ]
    
    def get_verified_content(self, min_score: float = 70.0) -> List[Dict[str, Any]]:
        """Get content blocks that meet verification threshold"""
        verified_blocks = [
            block for block in self.content_blocks 
            if block.verification_score >= min_score
        ]
        
        return [
            {
                "content_id": block.content_id,
                "text": block.text,
                "source": block.source,
                "metadata": block.metadata,
                "created_at": block.created_at.isoformat(),
                "verification_score": block.verification_score,
                "flags": block.flags
            }
            for block in verified_blocks
        ]
    
    def save_structured_content(self, output_path: str = "./content/structured/"):
        """Save structured content to file"""
        os.makedirs(output_path, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"structured_content_{timestamp}.json"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_structured_content(), f, indent=2, ensure_ascii=False)

        return filepath

# Global miner sanitizer instance
miner_sanitizer = KnowledgeMinerSanitizer()

def get_miner_sanitizer() -> KnowledgeMinerSanitizer:
    """Get the global miner sanitizer instance"""
    return miner_sanitizer

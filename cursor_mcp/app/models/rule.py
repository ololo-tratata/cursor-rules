from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class Rule(BaseModel):
    """Model representing a Cursor rule."""
    id: str
    technology: str
    file_patterns: List[str]
    content: Dict[str, Any]
    version: str
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "python-linting",
                "technology": "python",
                "file_patterns": ["*.py"],
                "content": {
                    "linters": ["flake8", "black"],
                    "rules": {"max_line_length": 88}
                },
                "version": "1.0.0",
                "updated_at": "2023-10-20T12:00:00"
            }
        }

class RuleSet(BaseModel):
    """Collection of rules with metadata."""
    rules: List[Rule]
    total: int
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

class FileContext(BaseModel):
    """Context information about a file."""
    file_path: str
    file_type: Optional[str] = None
    project_type: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None 
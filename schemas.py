# schemas.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ViolationType(str, Enum):
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    SEXUAL_CONTENT = "sexual_content"
    VIOLENCE = "violence"
    PROMPT_INJECTION = "prompt_injection"
    PII = "pii"

class SafetyCheckRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to validate.")
    project_id: Optional[str] = Field(None, description="User's project ID for tracking.")

class SafetyAnalysis(BaseModel):
    risk_score: float = Field(..., description="0.0 (Safe) to 1.0 (Unsafe).")
    detected_categories: List[ViolationType] = Field(default=[])

class Verdict(BaseModel):
    id: str
    allowed: bool
    # Optional: If you rewrite the prompt (e.g. remove PII), put it here.
    # If None, the user should use their original prompt.
    sanitized_prompt: Optional[str] = None 
    analysis: SafetyAnalysis
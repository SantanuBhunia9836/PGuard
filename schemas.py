from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# --- 1. The Enums (The most important part for SDKs) ---
# Stainless will turn these into strictly typed Enums.
# Users will type "ViolationType." and see these options automatically.
class ViolationType(str, Enum):
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    SEXUAL_CONTENT = "sexual_content"
    VIOLENCE = "violence"
    PROMPT_INJECTION = "prompt_injection"  # User tries to hack the LLM
    PII = "pii"                           # Personally Identifiable Information

# --- 2. The Request (Input) ---
# This defines the arguments for client.guard.check(...)
class SafetyCheckRequest(BaseModel):
    prompt: str = Field(
        ..., 
        description="The user prompt to validate against safety rules."
    )
    model: str = Field(
        "gpt-4", 
        description="The target LLM model. Used for specific heuristic adjustments."
    )
    # Example of an optional flag
    detect_pii: bool = Field(
        True, 
        description="Whether to scan for Personally Identifiable Information (phones, emails)."
    )

# --- 3. The Metadata (Reporting) ---
# Detailed info about WHY something was blocked.
class SafetyAnalysis(BaseModel):
    risk_score: float = Field(
        ..., 
        description="A score between 0.0 (Safe) and 1.0 (Dangerous)."
    )
    detected_categories: List[ViolationType] = Field(
        default=[], 
        description="List of specific violations found in the prompt."
    )

# --- 4. The Response (Output) ---
# This is what the user gets back: `response = client.guard.check(...)`
class SafetyCheckResponse(BaseModel):
    id: str = Field(..., description="Unique ID for this safety check.")
    
    allowed: bool = Field(
        ..., 
        description="Whether the prompt is safe to proceed."
    )
    
    # If allowed=True, this holds the safe prompt (or modified/spotlighted prompt)
    safe_prompt: Optional[str] = Field(
        None, 
        description="The sanitized prompt (if modified by Spotlight)."
    )
    
    # The analysis details
    analysis: SafetyAnalysis
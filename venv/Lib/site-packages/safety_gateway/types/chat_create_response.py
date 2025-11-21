# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ChatCreateResponse", "Analysis"]


class Analysis(BaseModel):
    risk_score: float
    """A score between 0.0 (Safe) and 1.0 (Dangerous)."""

    detected_categories: Optional[
        List[Literal["hate_speech", "self_harm", "sexual_content", "violence", "prompt_injection", "pii"]]
    ] = None
    """List of specific violations found in the prompt."""


class ChatCreateResponse(BaseModel):
    id: str
    """Unique ID for this safety check."""

    allowed: bool
    """Whether the prompt is safe to proceed."""

    analysis: Analysis

    safe_prompt: Optional[str] = None
    """The sanitized prompt (if modified by Spotlight)."""

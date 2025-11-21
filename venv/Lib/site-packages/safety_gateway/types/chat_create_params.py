# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ChatCreateParams"]


class ChatCreateParams(TypedDict, total=False):
    prompt: Required[str]
    """The user prompt to validate against safety rules."""

    detect_pii: bool
    """Whether to scan for Personally Identifiable Information (phones, emails)."""

    model: str
    """The target LLM model. Used for specific heuristic adjustments."""

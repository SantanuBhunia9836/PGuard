import re
import random
import asyncio
import uuid
from schemas import ViolationType, SafetyCheckResponse, SafetyAnalysis

# --- LAYER 1: The Fast Regex Guard ---
# This runs instantly. If it catches something, we don't bother checking the ML.
class RegexGuard:
    def __init__(self):
        # Real production systems have hundreds of these. 
        # We will add a few common "Jailbreak" patterns.
        self.patterns = {
            ViolationType.PROMPT_INJECTION: [
                r"ignore previous instructions",
                r"system override",
                r"DAN mode",
            ],
            ViolationType.PII: [
                r"\b\d{3}-\d{2}-\d{4}\b", # Simple SSN pattern
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", # Email pattern
            ]
        }

    def check(self, prompt: str):
        """Returns the first violation found, or None."""
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return category
        return None

# --- LAYER 2: The Smart ML Guard (Simulated) ---
# In real life, this would call a HuggingFace model or OpenAI Moderation API.
# We simulate it here to show how ASYNC works (crucial for performance).
class MLGuard:
    async def analyze(self, prompt: str):
        # Simulate "thinking" time (50ms)
        await asyncio.sleep(0.05) 
        
        # For testing purposes:
        # If the prompt contains "kill", we pretend the AI detected violence.
        if "kill" in prompt.lower():
            return ViolationType.VIOLENCE, 0.95  # Category, Confidence Score
        
        return None, 0.10 # Safe, Low risk score

# --- THE PIPELINE: Putting it together ---
class SafetyPipeline:
    def __init__(self):
        self.regex_guard = RegexGuard()
        self.ml_guard = MLGuard()

    async def run_check(self, prompt: str) -> SafetyCheckResponse:
        check_id = str(uuid.uuid4())
        
        # 1. Fast Check (Regex)
        regex_violation = self.regex_guard.check(prompt)
        if regex_violation:
            # FAIL FAST: Return immediately without running ML
            return SafetyCheckResponse(
                id=check_id,
                allowed=False,
                safe_prompt=None,
                analysis=SafetyAnalysis(
                    risk_score=1.0,
                    detected_categories=[regex_violation]
                )
            )

        # 2. Slow Check (ML) - Only runs if Regex passed
        ml_violation, score = await self.ml_guard.analyze(prompt)
        detected = []
        if ml_violation:
            detected.append(ml_violation)
            
        is_allowed = len(detected) == 0
        
        return SafetyCheckResponse(
            id=check_id,
            allowed=is_allowed,
            safe_prompt=prompt if is_allowed else None,
            analysis=SafetyAnalysis(
                risk_score=score,
                detected_categories=detected
            )
        )
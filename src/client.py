# client.py
import re
import requests
from typing import List, Optional
from dataclasses import dataclass

# Simple dataclass for the result (mirroring the API)
@dataclass
class GuardResult:
    allowed: bool
    reason: Optional[str] = None
    
class SafetyGateway:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        
        # --- LAYER 1: LOCAL INPUT REGEX ---
        # These run instantly on the client machine
        self.input_patterns = [
            re.compile(r"ignore previous instructions", re.IGNORECASE),
            re.compile(r"drop table", re.IGNORECASE), # SQLi Basic
        ]
        
        # --- LAYER 4: LOCAL OUTPUT PRIVACY PATTERNS ---
        # Empty by default. User populates this.
        self.private_patterns = []

    def add_private_pii(self, patterns: List[str]):
        """User adds secrets they want to block from leaving their server."""
        for p in patterns:
            self.private_patterns.append(re.compile(p, re.IGNORECASE))

    def check_input(self, prompt: str) -> GuardResult:
        """
        1. Checks Local Regex.
        2. If Safe, calls Remote API.
        """
        # 1. Local Check (Zero Latency)
        for pattern in self.input_patterns:
            if pattern.search(prompt):
                return GuardResult(False, "Local: Blocked by basic regex")\
                
        #2. scoring 

        # 2. Remote Check (Intelligence)  server
        try:
            resp = requests.post(
                f"{self.base_url}/v1/guard",
                json={"prompt": prompt, "project_id": self.api_key}
            )
            data = resp.json()
            return GuardResult(allowed=data['allowed'], reason=str(data.get('analysis')))
        except Exception as e:
            # FAIL OPEN or FAIL CLOSED? 
            # Usually better to fail open for connectivity issues, but log it.
            print(f"Gateway Error: {e}")
            return GuardResult(True, "Gateway Unreachable - Failed Open")

    def check_output(self, text: str) -> GuardResult:
        """
        Checks the LLM response against PRIVATE local patterns.
        """
        for pattern in self.private_patterns:
            if pattern.search(text):
                return GuardResult(False, "Blocked: Contains Private PII")
        
        return GuardResult(True)
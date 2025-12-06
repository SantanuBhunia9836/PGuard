# main.py
from fastapi import FastAPI
from schemas import SafetyCheckRequest, Verdict
from engine import SafetyPipeline
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Safety Gateway API")
pipeline = SafetyPipeline()

@app.post("/v1/guard", response_model=Verdict)
async def check_prompt(request: SafetyCheckRequest):
    """
    Returns {'allowed': True/False} based on the input.
    Does NOT generate the chat response.
    """
    return await pipeline.run_check(request.prompt)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
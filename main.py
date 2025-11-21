from fastapi import FastAPI
from schemas import SafetyCheckRequest, SafetyCheckResponse, SafetyAnalysis
from engine import SafetyPipeline
import uvicorn
import uuid
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load Environment Variables (Security)
load_dotenv()

# 2. Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env file!")
else:
    genai.configure(api_key=api_key)

app = FastAPI(title="Safety Gateway API")
pipeline = SafetyPipeline()

@app.post(
    "/v1/chat/completions", 
    response_model=SafetyCheckResponse,
    operation_id="chat_create" # Matches your client.chat.create() structure
)
async def analyze_and_proxy(request: SafetyCheckRequest):
    print(f"📥 Received prompt: {request.prompt}")

    # --- STEP A: Safety Check (Your Engine) ---
    safety_result = await pipeline.run_check(request.prompt)

    # If unsafe, BLOCK immediately. We never call Gemini.
    if not safety_result.allowed:
        print(f"🚫 Blocked! Reason: {safety_result.analysis.detected_categories}")
        return safety_result

    # --- STEP B: The Proxy (Real AI) ---
    print("✅ Safe. Calling Gemini...")
    
    try:
        # We use the 'gemini-pro' model (free tier compatible)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Call Gemini API
        response = model.generate_content(request.prompt)
        
        # Extract text
        real_answer = response.text
        
        # Attach the REAL answer to your safety response
        safety_result.safe_prompt = real_answer
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        safety_result.safe_prompt = "Error calling upstream LLM."

    return safety_result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
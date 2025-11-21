from fastapi import FastAPI
from schemas import SafetyCheckRequest, SafetyCheckResponse
from engine import SafetyPipeline
import uvicorn
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load Environment Variables
load_dotenv()

# 2. Configure Gemini (Used for the Responder step)
# Note: The Engine also configures its own internal Gemini client for the Judge step.
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env file! Real AI will fail.")
else:
    genai.configure(api_key=api_key)

app = FastAPI(title="Safety Gateway API")

# Initialize the pipeline (Regex + LLM Judge)
pipeline = SafetyPipeline() 

@app.post(
    "/v1/chat/completions", 
    response_model=SafetyCheckResponse, 
    operation_id="chat_create" # Matches client.chat.create()
)
async def analyze_and_proxy(request: SafetyCheckRequest):
    print(f"\n📥 New Request: {request.prompt}")

    # --- STEP 1: The Filter (Regex + LLM Judge) ---
    # This logic lives in engine.py. It checks for safety ONLY.
    safety_result = await pipeline.run_check(request.prompt)

    # If the Judge says "Unsafe", we block here.
    if not safety_result.allowed:
        print(f"🛑 BLOCKED by {safety_result.analysis.detected_categories}")
        # We return early. The "Responder" LLM is never called.
        return safety_result

    # --- STEP 2: The Responder (Only if Safe) ---
    print("✅ Safe. Generating Answer...")
    
    try:
        # This is the "User's LLM" or "Final LLM" that actually answers the question.
        # We use gemini-2.0-flash as the responder here.
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(request.prompt)
        
        # Attach the real answer to the safe result
        safety_result.safe_prompt = response.text
        print(f"🤖 AI Replied: {response.text[:50]}...")
        
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        safety_result.safe_prompt = f"Error generating response: {e}"

    return safety_result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
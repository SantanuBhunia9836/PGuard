import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("--- 🔍 Checking Available Gemini Models ---")
try:
    print(f"Key found: {api_key[:5]}...")
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found Model: {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ No text generation models found. Check your API Key permissions.")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")
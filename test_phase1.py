from schemas import SafetyCheckRequest, ViolationType

# Simulate a developer using your SDK (conceptually)
try:
    # 1. Try creating a valid request
    req = SafetyCheckRequest(prompt="Hello world")
    print("✅ Request Model works:", req)

    # 2. Check if Enum works
    print("✅ Enum Check:", ViolationType.PROMPT_INJECTION == "prompt_injection")

except Exception as e:
    print("❌ Something is wrong:", e)
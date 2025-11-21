# SDK Architecture - How It Works


### 1. Does `main.py` server need to be running when someone installs the SDK?

**Answer: NO** ❌

- **Installation time**: The server does NOT need to be running
- **Runtime (when making API calls)**: The server MUST be running ✅

**Explanation:**
- `pip install safety_gateway` only installs the SDK package (the client library)
- The SDK is just code that makes HTTP requests - it doesn't contain your backend logic
- Your server (`main.py`) only needs to run when someone actually uses the SDK to make API calls

---

### 2. How does the SDK access your backend?

**Answer: The SDK makes HTTP requests to your server**

The SDK is a **client** that sends HTTP requests to your **server**:

```
┌─────────────────┐         HTTP Request          ┌──────────────────┐
│   SDK Client     │ ────────────────────────────> │  Your Server     │
│  (safety_gateway)│                               │   (main.py)      │
│                  │ <──────────────────────────── │                  │
└─────────────────┘      HTTP Response            └──────────────────┘
```

**How it works:**

1. **SDK Configuration**: When creating the client, you specify the `base_url`:
   ```python
   from safety_gateway import SafetyGateway
   
   client = SafetyGateway(
       base_url="http://localhost:8000",  # Your server URL
       api_key="your-api-key"
   )
   ```

2. **SDK Makes HTTP Request**: When you call:
   ```python
   response = client.chat.completions.create(prompt="Hello")
   ```
   
   The SDK internally makes an HTTP POST request to:
   ```
   POST http://localhost:8000/v1/chat/completions
   Content-Type: application/json
   
   {
     "prompt": "Hello",
     "model": "gpt-4",
     "detect_pii": true
   }
   ```

3. **Your Server Responds**: Your `main.py` server receives the request, processes it, and returns a response

4. **SDK Returns Response**: The SDK parses the HTTP response and returns a Python object

---

### 3. Why didn't the SDK ask for your backend files?

**Answer: The SDK doesn't need your backend files - it only needs the OpenAPI spec!**

**Key Concept: Separation of Concerns**

The SDK generation process works like this:

```
┌─────────────────────────────────────────────────────────────┐
│                    SDK Generation Process                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. You provide: OpenAPI Spec (openapi.json)                 │
│     └─> This describes WHAT your API does                    │
│         - Endpoints                                           │
│         - Request/Response formats                            │
│         - Data types                                          │
│                                                               │
│  2. Stainless generates: SDK Code                            │
│     └─> This creates HOW to call your API                    │
│         - Client classes                                      │
│         - Request builders                                    │
│         - Response parsers                                    │
│                                                               │
│  3. Your backend files (main.py, engine.py, etc.)            │
│     └─> These contain the ACTUAL LOGIC                       │
│         - Business rules                                      │
│         - Safety checks                                       │
│         - Database operations                                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Why this design is good:**

1. **Security**: Your backend code stays on your server - never exposed to SDK users
2. **Simplicity**: SDK users only need to know the API contract (OpenAPI spec)
3. **Flexibility**: You can change backend implementation without changing the SDK
4. **Standard Practice**: This is how all major APIs work (OpenAI, Stripe, etc.)

**What the SDK contains:**
- ✅ HTTP client code (makes requests)
- ✅ Type definitions (from your OpenAPI spec)
- ✅ Request/Response serialization
- ✅ Error handling

**What the SDK does NOT contain:**
- ❌ Your `engine.py` safety logic
- ❌ Your `main.py` server code
- ❌ Your database connections
- ❌ Your business rules

---

### 4. What is the process now?

## Complete Workflow

### **Phase 1: Development & Testing (Local)**

```bash
# Terminal 1: Start your server
python main.py
# Server runs on http://localhost:8000

# Terminal 2: Use the SDK
python test_phase3.py
# SDK makes requests to http://localhost:8000
```

**Current Setup:**
1. ✅ Your server (`main.py`) is running locally
2. ✅ SDK is installed (`pip install safety_gateway`)
3. ✅ SDK configured to point to your server

**To test locally, update `test_phase3.py`:**

```python
from safety_gateway import SafetyGateway

# Point SDK to your local server
client = SafetyGateway(
    base_url="http://localhost:8000",  # Your local server
    api_key="test-key"  # If you add auth later
)

# Make API call
response = client.chat.completions.create(
    prompt="Hello, how are you?",
    model="gpt-4",
    detect_pii=True
)

print(f"Allowed: {response.allowed}")
print(f"Risk Score: {response.analysis.risk_score}")
```

---

### **Phase 2: Production Deployment**

**Step 1: Deploy Your Server**
- Deploy `main.py` to a server (AWS, Heroku, Railway, etc.)
- Example: `https://api.yourdomain.com`

**Step 2: Update OpenAPI Spec**
- Add production server URL to `openapi.json`:
  ```json
  {
    "servers": [
      {
        "url": "https://api.yourdomain.com",
        "description": "Production server"
      }
    ]
  }
  ```

**Step 3: Update SDK (if needed)**
- Regenerate SDK in Stainless with updated OpenAPI spec
- Or users can override `base_url` when creating client:
  ```python
  client = SafetyGateway(
      base_url="https://api.yourdomain.com",
      api_key="production-key"
  )
  ```

**Step 4: Publish SDK**
- Publish to PyPI: `pip install safety-gateway-sdk`
- Users install: `pip install safety-gateway-sdk`
- Users use SDK to call your deployed server

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    SDK User's Computer                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  User's Application Code                            │    │
│  │                                                      │    │
│  │  from safety_gateway import SafetyGateway           │    │
│  │  client = SafetyGateway(                            │    │
│  │      base_url="https://api.yourdomain.com"          │    │
│  │  )                                                   │    │
│  │  response = client.chat.completions.create(...)     │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                    │
│                          │ HTTP Request                      │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  SDK Package (safety_gateway)                      │    │
│  │  - Makes HTTP requests                             │    │
│  │  - Parses responses                                │    │
│  │  - Handles errors                                  │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                          │
                          │ Internet
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    Your Server (Cloud)                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  main.py (FastAPI Server)                          │    │
│  │  - Receives HTTP requests                          │    │
│  │  - Calls engine.py                                 │    │
│  │  - Returns JSON response                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  engine.py (Your Business Logic)                    │    │
│  │  - Safety checks                                    │    │
│  │  - Regex patterns                                   │    │
│  │  - ML analysis                                      │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **SDK = Client Library**: Just code that makes HTTP requests
2. **Server = Your Backend**: Contains all your business logic
3. **OpenAPI Spec = Contract**: Describes the API interface
4. **Separation**: SDK doesn't need your backend files, only the API contract
5. **Runtime**: Server must be running when SDK makes API calls

---

## Next Steps

1. **Test Locally**:
   ```bash
   # Terminal 1
   python main.py
   
   # Terminal 2
   python test_phase3.py  # Update with correct base_url
   ```

2. **Deploy Server**: Deploy `main.py` to a cloud service

3. **Update SDK Users**: Tell them to use:
   ```python
   client = SafetyGateway(base_url="https://api.yourdomain.com")
   ```

4. **Optional**: Add authentication to your API and SDK


# PGuard
PGuard: Our SDK based intelligent safety gateway to secure LLM applications.
🛡️ Safety Gateway SDK

An intelligent firewall for Large Language Models (LLMs).

The Safety Gateway is a middleware platform that sits between your users and powerful AI models (like Gemini or GPT-4). It intercepts prompts, scans them for malicious content (injections, PII, toxicity), and only forwards safe requests to the upstream LLM.

It comes with a Python SDK that is designed to be a drop-in replacement for the official OpenAI library.

🏗️ Architecture

The system uses a Cascading Defense strategy to filter attacks efficiently.

sequenceDiagram
    participant User as Client App (SDK)
    participant Gateway as Safety Gateway (FastAPI)
    participant Engine as Safety Engine
    participant LLM as Gemini 2.0 Flash

    User->>Gateway: client.chat.completions.create("prompt")
    
    rect rgb(255, 230, 230)
        Note over Gateway, Engine: 🛡️ The Safety Layer
        Gateway->>Engine: 1. Regex Check (Pre-computation)
        alt Regex Violation
            Engine-->>Gateway: 🛑 Blocked (Risk: 1.0)
            Gateway-->>User: Error: Prompt Injection Detected
        end
        
        Gateway->>Engine: 2. ML Classification (Mocked/Light)
        alt ML Violation
            Engine-->>Gateway: 🛑 Blocked (Risk: 0.8)
            Gateway-->>User: Error: Unsafe Content
        end
    end

    rect rgb(230, 255, 230)
        Note over Gateway, LLM: ✅ Safe Path
        Gateway->>LLM: Forward Prompt (Proxy)
        LLM-->>Gateway: AI Response
    end

    Gateway-->>User: Return Safe Response (Risk: 0.0)


🚀 Features

Drop-in Compatibility: The SDK mimics the client.chat.completions.create syntax used by OpenAI, making migration zero-effort.

Cascading Filters:

Layer 1 (Regex): Instantly blocks known jailbreaks (e.g., "Ignore previous instructions") and PII (SSNs, Emails).

Layer 2 (ML): (Simulated) semantic analysis for deeper threats.

Real Intelligence: Integrated with Google's Gemini 2.0 Flash for high-speed, low-cost responses.

Typed SDK: Fully typed Python library generated via Stainless API, offering autocomplete and strict validation.

🛠️ The Development Journey

We built this system in 5 Phases:

Phase 1: The Contract (Schema First)

We defined the "Rules of Engagement" using Pydantic Models. This ensured that Stainless (our SDK generator) understood exactly what data looks like.

Key Output: schemas.py defining SafetyCheckRequest and SafetyCheckResponse.

Phase 2: The Logic Engine

We built the filtering brain.

Key Output: engine.py containing RegexGuard and MLGuard.

Strategy: Fail Fast. If Regex catches a threat, we never pay the cost of the ML check.

Phase 3: The Proxy Server

We wrapped the logic in a FastAPI web server.

Key Output: main.py.

Integration: Connected to Google Gemini API to provide real answers for safe prompts.

Phase 4: SDK Generation

We used Stainless API to convert our openapi.json into a professional Python library.

Key Config: stainless.yaml mapping /v1/chat/completions to client.chat.create.

Phase 5: Distribution

We published the SDK to a package registry (simulated via Git install) so users can install it with one command.

Command: pip install safety_gateway

📂 Project Structure

safety-gateway/
├── main.py          # 🚀 The API Server (FastAPI) entry point
├── engine.py        # 🧠 The Logic (Regex & Safety Pipelines)
├── schemas.py       # 📜 The Data Contracts (Pydantic Models)
├── stainless.yaml   # ⚙️ Configuration for SDK Generation
├── openapi.json     # 📄 Auto-generated API Spec (fed to Stainless)
└── .env             # 🔑 Secrets (Gemini API Key)


⚡ Quickstart

1. Start the Server

# Install dependencies
pip install fastapi uvicorn google-generativeai python-dotenv

# Run the Gateway
python main.py


2. Use the SDK

from safety_gateway import SafetyGateway

# Point to your local gateway instead of OpenAI
client = SafetyGateway(base_url="http://localhost:8000")

response = client.chat.create(
    prompt="Why is the sky blue?",
    model="gpt-4"
)

if response.allowed:
    print("🤖 AI:", response.safe_prompt)
else:
    print("🛑 Blocked:", response.analysis.detected_categories)


🛣️ Production Roadmap (What's Next)

To take this from a "Working Prototype" to a "SaaS Product", we need to implement the following layers:

1. Authentication (The Gatekeeper)

Current State: No auth. Anyone can call the API.

Next Step: Implement API Keys (sk-live-...).

Tech: Redis or PostgreSQL to store active keys and validate them in FastAPI middleware.

2. Rate Limiting

Problem: One user could spam 1,000 requests/sec and bankrupt your Gemini account.

Next Step: Use Redis to track usage per API key (e.g., 60 requests/minute).

3. Analytics Dashboard

Value Prop: Security teams need to see what was blocked.

Next Step: Log every SafetyAnalysis object to a database (ClickHouse or Postgres). Build a frontend to show "Attacks Blocked Today".

4. Deployment (DevOps)

Current State: Running on localhost.

Next Step: Dockerize the application (Dockerfile). Deploy to a cloud provider like AWS, Render, or Railway behind a load balancer.
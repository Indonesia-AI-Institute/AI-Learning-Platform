# 📘 AI Learning Platform --- Backend API

Backend service untuk **AI Learning Platform** yang menyediakan Chat API
berbasis LLM dengan support:

-   Streaming response (SSE)
-   Non-stream response (REST)
-   Guardrail filtering
-   Provider abstraction (future multi-provider ready)
-   Clean service architecture

------------------------------------------------------------------------

# 🚀 Tech Stack

-   **FastAPI** --- Web framework
-   **Uvicorn** --- ASGI server
-   **Pydantic Settings** --- Config management
-   **OpenAI SDK** --- LLM Provider
-   **Python 3.11+ (Recommended)**

------------------------------------------------------------------------

# 📂 Project Structure

    src/backend
    |    │
    |    ├── api/
    |    │   └── v1/
    |    │       └── chat_routes.py
    |    │
    |    ├── core/
    |    │   ├── config.py
    |    │   └── constants.py
    |    │
    |    ├── llm/
    |    │   ├── providers/
    |    ││   ├── service/
    |    │   │   └── llm_service.py
    |    │   └── base/
    |    │
    |    ├── services/
    |    │   └── chat_service.py
    |    │
    |    ├── schemas/
    |    │   └── chat/
    |    │
    |    ├── guardrails/
    |    │
    |    ├── utils/
    |    │
    |    └── main.py
    |    ├── .env_example
    |── requirements.txt
------------------------------------------------------------------------

# ⚙️ Requirements

### Python

Disarankan:

    Python 3.11

Hindari:

    Python 3.13+

------------------------------------------------------------------------

# 🧪 Setup Local Development

## 1️⃣ Clone Repository

``` bash
git clone https://github.com/Indonesia-AI-Institute/AI-Learning-Platform.git
```

## 2️⃣ Create Virtual Environment

### UV (Recommended)

``` bash
uv venv --python 3.11
.venv/Scripts/Activate
```

### Windows

``` bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac / Linux

``` bash
python -m venv .venv
source .venv/bin/activate
```

## 3️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```
or 

``` bash
uv pip install -r requirements.txt
```

------------------------------------------------------------------------

# ▶️ Run Backend
``` bash
cd ./src/backend
```
``` bash
uvicorn main:app --reload
```

Default:

    http://localhost:8000

Swagger Docs:

    http://localhost:8000/docs

------------------------------------------------------------------------

# 💬 Chat API Endpoints

## 🔹 Streaming Chat (Primary Mode)

### Endpoint

    POST /api/v1/chat/stream

### Example Request

``` json
{
  "user_prompt": "Explain neural network simply",
  "system_prompt": "You are an AI tutor",
  "chat_history": []
}
```

------------------------------------------------------------------------

## 🔹 Generate Chat (Non Streaming)

### Endpoint

    POST /api/v1/chat/generate

### Example Response

``` json
{
  "response_text": "Neural networks are...",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20
  },
  "model": "gpt-4o"
}
```

------------------------------------------------------------------------

# 🧠 Architecture Overview

    Route Layer
        ↓
    Chat Service (Business Logic)
        ↓
    LLM Service (Provider Orchestration)
        ↓
    LLM Provider (OpenAI / Future Multi Provider)

------------------------------------------------------------------------

# 🛡 Guardrail Support

Banlist filter aktif via config:

``` env
ENABLE_BANLIST_FILTER=true
```

Default banned keywords: - illegal - exploit - bypass

------------------------------------------------------------------------

# 🧪 Testing via Swagger

Buka:

    /docs

Test: - `/chat/stream` - `/chat/generate`

------------------------------------------------------------------------

# 🧯 Troubleshooting

## ❌ Error: OPENAI_API_KEY None

Check: - `.env` ada di root backend - config.py pakai env_file=".env"

------------------------------------------------------------------------

## ❌ Streaming Jalan Tapi Generate Tidak

Biasanya karena: - Provider return format beda - ChatResponse schema
mismatch

Sudah difix via response normalization di chat_service.

------------------------------------------------------------------------

# 📈 Future Roadmap

-   Multi Provider Routing
-   Cost Tracking
-   Conversation Memory
-   RAG Integration
-   Tool Calling
-   Analytics Dashboard

------------------------------------------------------------------------

# 🧾 License

Internal Use --- AI Learning Platform

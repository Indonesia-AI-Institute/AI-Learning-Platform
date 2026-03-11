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
    AI learning platform/
    |
    ├── alembic/
    |   ├── versions/
        |   └──xxxxx_(version).py
    |   ├── env.py
    |   ├── README.md
    |   └── script.py.mako
    ├── .venv/
    ├── src/
    |    └──backend/
    |       ├── auth/
    |       |   └──security.py
    |       ├── models/
    |       |   ├── __init__.py
    |       |   ├── base.py 
    |       |   ├── chat_history.py
    |       |   ├── chat_session.py
    |       |   ├── class_model.py
    |       |   ├── course.py
    |       |   ├── enrollment.py
    |       |   ├── task.py
    |       |   ├── session_analytics.py
    |       |   ├── token_blacklist.py
    |       |   └── user.py
    |       |
    |       ├── api/
    |       │   ├── v1/
    |       │   |   ├── chat_routes.py
    |       |   |   ├── auth_routes.py
    |       |   |   ├── analytics_routes.py
    |       |   |   ├── class_routes.py
    |       |   |   ├── course_routes.py
    |       |   |   ├── enrollment_routes.py
    |       |   |   ├── task_routes.py
    |       │   |   └── health_routes.py
    |       |   ├── deps.py
    |       |   └── router.py
    |       |    
    |       ├── core/
    |       │   ├── config.py
    |       │   └── constants.py
    |       │
    |       ├── db/
    |       |   ├── init_db.py
    |       |   ├── base.py
    |       |   └── session.py
    |       |
    |       ├── guardrails/
    |       │   └── banlist_filter.py
    |       |
    |       ├──  agents/
    |       |     ├── prompts/
    |       |     |       ├── socratic_tutor.yaml
    |       |     |       └── direct_tutor.yaml
    |       |     |
    |       |     ├── services/
    |       |     |       ├── socratic_agent.py
    |       |     |       ├── base_agent.py
    |       |     |       └── direct_agent.py
    |       |     └── registry/
    |       |             ├── agent_registry.py
    |       |             └── agent_factory.py
    |       ├── llm/
    |       │   ├── providers/
    |       │   |   ├── __init__.py
    |       │   |   └── openai_providers.py 
    |       │   |
    |       │   ├── services/
    |       │   │   └── llm_service.py
    |       │   └── base/
    |       │       └── llm_providers.py
    |       │
    |       ├── observability/
    |       |   ├── logger.py
    |       |   └── logging_config.py
    |       │
    |       ├── services/
    |       |   ├── auth_service.py
    |       │   ├── chat_service.py
    |       |   ├── chat_history_service.py
    |       |   ├── class_service.py
    |       |   ├── context_window_service.py
    |       |   ├── conversation_service.py
    |       |   ├── course_service.py
    |       |   ├── enrollment_service.py
    |       |   ├── session_analytics_service.py
    |       |   ├── session_service.py
    |       |   └── task_service.py
    |       |
    |       ├── repositories/
    |       |   ├── base_repository.py
    |       |   ├── chat_history_repository.py
    |       |   ├── class_repository.py
    |       |   ├── course_repository.py
    |       |   ├── session_repository.py
    |       |   ├── task_repository.py
    |       |   ├── token_blacklist_repository.py
    |       |   ├── enrollment_repository.py
    |       |   └── user_repository.py
    |       │
    |       ├── schemas/
    |       │   ├── chat/
    |       |   |    ├── chat_history_response.py
    |       │   |    ├──  chat_request.py
    |       │   |    ├──  chat_response.py
    |       |   |    ├── chat_session_response
    |       │   |    └── chat_stream_chunk.py
    |       |   ├── analytics/
    |       |   |    └── analytics_response.py
    |       |   ├── auth/
    |       |   |    ├── login_requst.py
    |       |   |    ├── register_request.py
    |       |   |    ├── token_request.py
    |       |   |    └── user_response.py
    |       |   ├── classes/
    |       |   |    ├── class_crate.py
    |       |   |    ├── class_response.py
    |       |   |    └── class_update.py
    |       |   ├── course/
    |       |   |    ├── course_crate.py
    |       |   |    ├── course_response.py
    |       |   |    └── course_update.py
    |       |   ├── task/
    |       |   |    ├── task_crate.py
    |       |   |    ├── task_response.py
    |       |   |    └── task_update.py
    |       |   ├── enrollment/
    |       |   |    ├── enrollment_crate.py
    |       |   |    └── enrollment_response.py
    |       ├── utils/
    |       │   └── streaming_utils.py
    |       └──main.py
    ├── alembic.ini
    ├── .dockerignore
    ├── .env_example
    ├── docker-compose.yml
    ├── Dockerfile
    ├── README.md
    └── requirements.txt
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

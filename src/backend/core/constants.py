"""
constants.py
============

Global constants untuk AI Learning Platform Backend.

Tujuan:
- Menyimpan constant values yang sering dipakai
- Menghindari hardcode string di banyak file
- Memudahkan maintenance dan scaling

NOTE:
File ini hanya untuk CONSTANT.
Bukan config env → itu di config.py
"""

# ======================================================
# LLM DEFAULT CONFIG
# ======================================================

# Default provider name (dipakai di registry lookup)
DEFAULT_LLM_PROVIDER = "openai"

# Default model (OpenAI)
DEFAULT_OPENAI_MODEL = "gpt-4o"

# Default generation parameters
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT = 60


# ======================================================
# CHAT ROLE CONSTANTS
# ======================================================

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"


# ======================================================
# SSE EVENT CONSTANTS
# ======================================================

# Event name untuk token streaming
SSE_EVENT_TOKEN = "token"

# Event name untuk stream selesai
SSE_EVENT_DONE = "done"

# Event name untuk error
SSE_EVENT_ERROR = "error"


# ======================================================
# GUARDRAIL CONSTANTS
# ======================================================

# Guardrail response message (generic)
GUARDRAIL_BLOCK_MESSAGE = "Your prompt contains restricted content."

# Optional: Max prompt length protection
MAX_PROMPT_LENGTH = 20000


# ======================================================
# API CONSTANTS
# ======================================================

# API Version
API_V1_PREFIX = "/api/v1"

# Chat route base path
CHAT_ROUTE_PREFIX = "/chat"


# ======================================================
# PROJECT META
# ======================================================

PROJECT_NAME = "AI Learning Platform"
PROJECT_VERSION = "0.1.0"
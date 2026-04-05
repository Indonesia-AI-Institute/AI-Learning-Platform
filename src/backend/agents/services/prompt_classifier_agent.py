"""
agents/services/prompt_classifier_agent.py
==========================================

Classifies student prompts into predefined categories.
Runs in parallel with chat response — does NOT affect chat latency.
"""

import json
from typing import Dict

from src.backend.llm.services.llm_service import LLMService
from src.backend.observability.logging.logger import get_logger

logger = get_logger(__name__)

CLASSIFIER_SYSTEM_PROMPT = """You are a prompt classification system for an AI learning platform.

Your task is to classify a student's message into one or more of these categories:

- direct_answer: Student wants a direct answer without explanation ("Give me the answer", "What is X?", "Tell me the result")
- explanation: Student wants concept explanation ("Explain", "What does X mean?", "Why is X?")
- step_by_step: Student wants step-by-step guidance ("How to solve", "Walk me through", "Show the steps")
- example: Student wants an example ("Give me an example", "Show similar case", "Can you illustrate?")
- rewrite: Student wants their work rewritten or improved ("Rewrite this", "Fix my answer", "Improve my text")
- feedback: Student wants feedback on their work ("Check my answer", "Is this correct?", "Review my work")
- summary: Student wants a summary ("Summarize", "TL;DR", "Give me the key points")
- translation: Student wants translation ("Translate this", "In English:", "What is this in Indonesian?")
- brainstorm: Student wants ideas ("Give me ideas", "Brainstorm", "What are some options?")

Respond ONLY with a valid JSON object. No explanation, no markdown, no extra text.

Example output:
{"direct_answer": false, "explanation": true, "step_by_step": false, "example": false, "rewrite": false, "feedback": false, "summary": false, "translation": false, "brainstorm": false}
"""


class PromptClassifierAgent:
    """
    Lightweight agent to classify prompt types.
    Uses a separate LLM call — isolated from chat context.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def classify(self, prompt: str) -> Dict[str, bool]:
        """
        Classify a student prompt and return boolean flags.
        Returns default (all False) if classification fails.
        """

        default_result = {
            "direct_answer": False,
            "explanation": False,
            "step_by_step": False,
            "example": False,
            "rewrite": False,
            "feedback": False,
            "summary": False,
            "translation": False,
            "brainstorm": False,
        }

        try:
            messages = [
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify this student message:\n\n{prompt}"},
            ]

            response = await self.llm_service.generate(messages=messages)
            raw = response.get("content", "").strip()

            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)

            # Validate and sanitize — ensure all keys are booleans
            sanitized = {}
            for key in default_result:
                sanitized[key] = bool(result.get(key, False))

            return sanitized

        except Exception as e:
            logger.warning(
                "prompt_classifier.failed",
                extra={
                    "event": "prompt_classifier.failed",
                    "error": str(e),
                    "prompt_preview": prompt[:100],
                },
            )
            return default_result
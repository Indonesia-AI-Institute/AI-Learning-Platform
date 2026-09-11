import asyncio
import time
from typing import Any, AsyncGenerator, Dict
from uuid import UUID

from backend.agents.services.prompt_classifier_agent import PromptClassifierAgent
from backend.llm.services.llm_service import LLMService
from backend.models.user import User
from backend.observability.logging.logger import get_logger
from backend.services.chat_history_service import ChatHistoryService
from backend.services.chat_service import ChatService
from backend.services.prompt_classification_service import PromptClassificationService
from backend.services.session_service import SessionService

logger = get_logger(__name__)


class ConversationService:
    """
    AI Conversation Orchestration Layer.
    """

    def __init__(
        self,
        session_service: SessionService,
        history_service: ChatHistoryService,
        chat_service: ChatService,
        classification_service: PromptClassificationService,
        llm_service: LLMService,
    ):
        self.session_service = session_service
        self.history_service = history_service
        self.chat_service = chat_service
        self.classification_service = classification_service
        self.classifier_agent = PromptClassifierAgent(llm_service)

    async def _classify_and_save(
        self,
        content: str,
        chat_history_id: UUID,
        session_id: UUID,
        student_id: UUID,
        task_id: UUID,
    ):
        """
        Classify prompt and save result.
        Called in parallel — errors are logged, never raised.
        """
        try:
            flags = await self.classifier_agent.classify(content)
            await self.classification_service.save_classification(
                chat_history_id=chat_history_id,
                session_id=session_id,
                student_id=student_id,
                task_id=task_id,
                flags=flags,
            )
        except Exception as e:
            logger.warning(
                "conversation.classification_failed",
                extra={"event": "conversation.classification_failed", "error": str(e)},
            )

    async def send_message(
        self,
        current_user: User,
        session_id: UUID,
        agent_type: str,
        content: str,
        system_prompt: str | None = None,
        **agent_kwargs: Any,
    ) -> Dict[str, Any]:

        db_session = await self.session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )

        if not db_session.is_active:
            raise ValueError("Session is not active.")

        user_message = await self.history_service.add_user_message(
            session_id=session_id,
            user_id=current_user.id,
            content=content,
        )

        messages = await self.history_service.build_llm_context(
            session_id=session_id,
            include_system_prompt=system_prompt,
        )

        start_time = time.time()

        ai_response, _ = await asyncio.gather(
            self.chat_service.generate(
                agent_type=agent_type,
                messages=messages,
                **agent_kwargs,
            ),
            self._classify_and_save(
                content=content,
                chat_history_id=user_message.id,
                session_id=session_id,
                student_id=current_user.id,
                task_id=db_session.task_id,
            ),
        )

        latency = int((time.time() - start_time) * 1000)
        assistant_content = ai_response.get("content")
        usage = ai_response.get("usage", {})

        assistant_message = await self.history_service.create_assistant_message(
            session_id=session_id,
            model_name=ai_response.get("model"),
            provider_name=ai_response.get("provider"),
        )

        await self.history_service.finalize_assistant_message(
            message_id=assistant_message.id,
            content=assistant_content,
            input_tokens=usage.get("prompt_tokens") or 0,
            output_tokens=usage.get("completion_tokens") or 0,
            latency_ms=latency,
            metadata=ai_response.get("metadata"),
        )

        return ai_response

    async def stream_message(
        self,
        current_user: User,
        session_id: UUID,
        agent_type: str,
        content: str,
        system_prompt: str | None = None,
        **agent_kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        db_session = await self.session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )

        if not db_session.is_active:
            raise ValueError("Session is not active.")

        user_message = await self.history_service.add_user_message(
            session_id=session_id,
            user_id=current_user.id,
            content=content,
        )

        messages = await self.history_service.build_llm_context(
            session_id=session_id,
            include_system_prompt=system_prompt,
        )

        assistant_message = await self.history_service.create_assistant_message(
            session_id=session_id,
            model_name=None,
            provider_name=None,
        )

        # Fire-and-forget: classification runs in the background so it
        # doesn't block the token stream.
        asyncio.create_task(
            self._classify_and_save(
                content=content,
                chat_history_id=user_message.id,
                session_id=session_id,
                student_id=current_user.id,
                task_id=db_session.task_id,
            )
        )

        start_time = time.time()
        full_response = ""
        token_buffer = ""
        usage = {}
        finish_reason = None
        model_name = None
        provider_name = None
        BUFFER_SIZE = 20

        async for event in self.chat_service.stream_generate(
            agent_type=agent_type,
            messages=messages,
            **agent_kwargs,
        ):

            if event["type"] == "token":
                token = event["content"]
                full_response += token
                token_buffer += token
                yield token

                if len(token_buffer) >= BUFFER_SIZE:
                    await self.history_service.update_streaming_content(
                        message_id=assistant_message.id,
                        partial_content=token_buffer,
                    )
                    token_buffer = ""

            elif event["type"] == "start":
                model_name = event.get("model")
                provider_name = event.get("provider")
                await self.history_service.set_model_provider(
                    message_id=assistant_message.id,
                    model_name=model_name,
                    provider_name=provider_name,
                )

            elif event["type"] == "done":
                usage = event.get("usage", {})
                finish_reason = event.get("finish_reason")

        # Save remaining buffer
        if token_buffer:
            await self.history_service.update_streaming_content(
                message_id=assistant_message.id,
                partial_content=token_buffer,
            )

        latency = int((time.time() - start_time) * 1000)

        await self.history_service.finalize_assistant_message(
            message_id=assistant_message.id,
            content=full_response,
            input_tokens=usage.get("prompt_tokens") or 0,
            output_tokens=usage.get("completion_tokens") or 0,
            latency_ms=latency,
            metadata={"finish_reason": finish_reason},
        )
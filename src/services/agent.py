import logging
from typing import Optional, Protocol

from g4f import Client
from g4f.typing import Message

from src.core.config import Settings
from src.schemas.agent import ResponseSchema, AgentConfig
from src.core.errors.agent import AgentException

logger = logging.getLogger(__name__)


class AIClient(Protocol):
    """Protocol for the AI client so that the implementation can be easily replaced"""

    def chat_completion(
            self,
            model: str,
            messages: list,
            web_search: bool,
    ) -> str:
        ...


class G4FClientAdapter:
    """Adapter for G4F client"""

    def __init__(self):
        self._client = Client()

    def chat_completion(
            self,
            model: str,
            messages: list,
            web_search: bool,
    ) -> str:
        try:
            completion = self._client.chat.completions.create(
                model=model,
                messages=messages,
                web_search=web_search,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to get completion: {e}")
            raise AgentException(f"AI service error: {e}")


class Agent:
    def __init__(
            self,
            config: Optional[AgentConfig] = None,
            settings: Optional[Settings] = None,
            ai_client: Optional[AIClient] = None,
    ):
        self.settings = settings or Settings()  # noqa
        self.config = config or self._create_default_config()
        self.ai_client = ai_client or G4FClientAdapter()
        logger.info(f"Agent initialized with model: {self.config.model}")


    def _create_default_config(self) -> AgentConfig:
        settings = self.settings
        return AgentConfig(
            model=settings.DEFAULT_MODEL,
            web_search=False,
            settings=settings
        )

    def send_message(self, message: str) -> ResponseSchema:
        """Sends a message to the agent and receives a response"""
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        logger.debug("Sending message to agent: %s", message[:100])

        try:
            completion = self.ai_client.chat_completion(
                model=self.config.model,
                messages=[Message(role="user", content=message)],
                web_search=self.config.web_search,
            )

            logger.debug("Received response from agent")
            return ResponseSchema(message=completion)

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise AgentException(f"Failed to communicate with AI: {e}")

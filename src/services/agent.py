import logging
from typing import Optional

from g4f import Client
from g4f.typing import Message

from src.core.config import Settings
from src.schemas.agent import ResponseSchema

logger = logging.getLogger(__name__)


class Agent:
    def __init__(
            self,
            settings: Settings = None,
            web_search: bool = False,
            model: Optional[str] = None,
    ):
        logger.info("Initializing agent")
        self.settings = settings or Settings()  # noqa
        self.model = model or settings.DEFAULT_MODEL
        self.web_search = web_search
        self.client = Client()
        logger.info("Agent initialized")

    def send_msg_to_agent(self, message: str) -> ResponseSchema:
        logger.info("Sending message to agent: %s", message)
        completion = self.client.chat.completions.create(
            modle=self.model,
            messages=[Message(role="user", content=message)],
            web_search=self.web_search,
        )
        logger.info("Response from agent: %s", completion)
        response = ResponseSchema(message=completion.choices[0].message.content)
        return response

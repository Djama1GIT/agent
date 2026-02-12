from typing import Optional

from g4f import Client
from g4f.typing import Message

from src.core.config import Settings
from src.schemas.agent import ResponseSchema


class Agent:
    def __init__(
            self,
            settings: Settings = None,
            web_search: bool = False,
            model: Optional[str] = None,
    ):
        self.settings = settings or Settings()  # noqa
        self.model = model or settings.DEFAULT_MODEL
        self.web_search = web_search
        self.client = Client()

    def send_msg_to_agent(self, message: str) -> ResponseSchema:
        completion = self.client.chat.completions.create(
            modle=self.model,
            messages=[Message(role="user", content=message)],
            web_search=self.web_search,
        )
        response = ResponseSchema(message=completion.choices[0].message.content)
        return response

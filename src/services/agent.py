from g4f import Client
from g4f.typing import Message


class Agent:
    def __init__(self, model: str = "gpt_4o", web_search: bool = False):
        self.model = model
        self.web_search = web_search
        self.client = Client()

    def msg(self, message: str) -> str:
        response = self.client.chat.completions.create(
            modle=self.model,
            messages=[Message(role="user", content=message)],
            web_search=self.web_search,
        )
        return response.choices[0].message.content

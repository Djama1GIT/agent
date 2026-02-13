from typing import Optional

from pydantic import BaseModel

from src.core.config import Settings


class AgentConfig(BaseModel):
    """Agent Configuration"""
    model: str
    web_search: bool = False
    settings: Optional[Settings] = None


class ResponseSchema(BaseModel):
    message: str

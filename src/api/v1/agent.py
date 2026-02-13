import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.agent import get_agent
from src.dependencies.settings import get_settings
from src.schemas.agent import ResponseSchema
from src.services.agent import Agent

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


@router.post("/", response_model=ResponseSchema)
async def send_message(
        message: str,
        agent: Annotated[Agent, Depends(get_agent(get_settings))],
) -> ResponseSchema:
    logger.info(f"Sending message: {message}")

    response = agent.send_msg_to_agent(message)

    logger.info(f"Received response: {response}")
    return response

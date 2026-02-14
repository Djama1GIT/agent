"""Agent API endpoints for handling chat interactions."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

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
        agent: Annotated[Agent, Depends(get_agent(get_settings))],
        message: str = Query(
            ...,
            description="The user's message text to send to the agent",
            examples=["What is the weather today?"],
        ),
) -> ResponseSchema:
    """Send a message to the agent and get a response.

    Args:
        message: The user's message to send to the agent.
        agent: Injected agent instance with configured settings

    Returns:
        ResponseSchema containing the agent's response message
    """
    logger.info(f"Sending message: {message}")

    response = agent.send_message(message)

    logger.info(f"Received response: {response}")
    return response

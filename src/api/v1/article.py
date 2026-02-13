import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.article import get_article_agent
from src.dependencies.settings import get_settings
from src.schemas.article import ArticleSchema
from src.services.article_agent import ArticleAgent

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/article-agent",
    tags=["Article Agent"],
)


@router.post("/", response_model=ArticleSchema)
async def create_article(
        article_name: str,
        article_agent: Annotated[ArticleAgent, Depends(get_article_agent(get_settings))],
) -> ArticleSchema:
    logger.info(f"Generating article: {article_name}")

    article = article_agent.generate(article_name)

    logger.info(f"Generated article: {article.summary[:100]}...")
    return article

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

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
        article_agent: Annotated[ArticleAgent, Depends(get_article_agent(get_settings))],
        article_name: str = Query(
            ...,
            description="The topic name of the article",
            examples=["P.E.T.Y.A."],
        ),
) -> ArticleSchema:
    """Generate an article based on the provided topic name.

    Creates a comprehensive article using the article agent, which leverages
    AI to research and generate content about the specified topic.

    Args:
        article_name: The topic or title of the article to generate
        article_agent: Injected article agent instance with configured settings

    Returns:
        ArticleSchema containing the generated article with summary,
        and full content
    """
    logger.info(f"Generating article: {article_name}")

    article = article_agent.generate(article_name)

    logger.info(f"Generated article: {article.summary[:100]}...")
    return article

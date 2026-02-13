import logging

from src.schemas.article import ArticleSchema
from src.services.agent import Agent

logger = logging.getLogger(__name__)


class ArticleAgent(Agent):
    prompt = "Сгенерируй статью с названием: {title}. Первый абзац должен быть " \
             "кратким описанием - сводка, самостоятельный абзац. " \
             "Со следующего абзаца должна начинаться статья без контекста сводки. " \
             "Вначале и в конце не должно быть никаких утверждений и вопросов, помимо статьи. " \
             "Статья должна быть на русском языке."

    def generate(self, title: str) -> ArticleSchema:
        logger.info("Generating article: %s", title)
        response = self.send_msg_to_agent(ArticleAgent.prompt.format(title=title))
        article = ArticleSchema(
            summary="",
            article=response.message,
        )
        logger.info(f"Generated article: {article.summary}")
        return article

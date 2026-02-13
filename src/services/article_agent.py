import logging

from src.schemas.article import ArticleSchema
from src.services.agent import Agent

logger = logging.getLogger(__name__)


class ArticleAgent(Agent):
    prompt = "Сгенерируй статью с названием: {title}. " \
             "Первый абзац, c первого слова должен быть " \
             "кратким описанием - сводка, самостоятельный абзац. " \
             "Не пиши где сводка, где текст. " \
             "Просто информация о статье которую спарсит код. " \
             "Со следующего абзаца должна начинаться статья без контекста сводки. " \
             "Вначале и в конце не должно быть никаких утверждений и вопросов, помимо статьи. " \
             "Статья должна быть на русском языке."

    def generate(self, title: str) -> ArticleSchema:
        logger.info("Generating article: %s", title)
        response = self.send_msg_to_agent(ArticleAgent.prompt.format(title=title))

        full_text = response.message
        paragraphs = full_text.split('\n\n')

        if paragraphs:
            summary = paragraphs[0].strip()
            article_text = '\n\n'.join(paragraphs[1:]).strip()
        else:
            summary = ""
            article_text = full_text

        article = ArticleSchema(
            summary=summary,
            article=article_text,
        )
        logger.info(f"Generated article summary: {article.summary[:100]}...")
        return article

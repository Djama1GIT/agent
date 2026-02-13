import logging
from typing import Optional

from src.schemas.article import ArticleSchema
from src.services.agent import Agent, AgentConfig
from src.core.errors.article import ArticleGenerationException

logger = logging.getLogger(__name__)


class ArticlePrompt:
    """Managing prompts for generating articles"""

    DEFAULT_TEMPLATE = (
        "Сгенерируй статью с названием: {title}. "
        "Первый абзац, c первого слова должен быть "
        "кратким описанием - сводка, самостоятельный абзац. "
        "Не пиши где сводка, где текст. "
        "Просто информация о статье которую спарсит код. "
        "Со следующего абзаца должна начинаться статья без контекста сводки. "
        "Вначале и в конце не должно быть никаких утверждений и вопросов, помимо статьи. "
        "Статья должна быть на языке: {language}."
    )

    def __init__(self, template: Optional[str] = None):
        self.template = template or self.DEFAULT_TEMPLATE

    def format(self, title: str, language: str = "русский") -> str:
        return self.template.format(title=title, language=language)


class ArticleAgent(Agent):
    """Article generation agent"""

    def __init__(
            self,
            config: Optional[AgentConfig] = None,
            prompt_template: Optional[str] = None,
            language: str = "русский",
            min_paragraphs: int = 2,
    ):
        super().__init__(config)
        self.prompt = ArticlePrompt(prompt_template)
        self.language = language
        self.min_paragraphs = min_paragraphs

    def generate(self, title: str) -> ArticleSchema:
        """Generates an article based on the title"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        logger.info(f"Generating article: '{title}' in {self.language}")

        try:
            response = self.send_message(
                self.prompt.format(title=title, language=self.language)
            )

            summary, article_text = self._parse_article(response.message)
            self._validate_article(summary, article_text)

            article = ArticleSchema(
                summary=summary,
                article=article_text,
            )

            logger.info(f"Successfully generated article. "
                        f"Summary length: {len(summary)}, "
                        f"Article length: {len(article_text)}")

            return article

        except Exception as e:
            logger.error(f"Failed to generate article '{title}': {e}")
            raise ArticleGenerationException(f"Article generation failed: {e}")

    @staticmethod
    def _parse_article(full_text: str) -> tuple[str, str]:
        """Parses the full text into summary and the main part"""
        paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]

        if len(paragraphs) >= 2:
            summary = paragraphs[0]
            article_text = '\n\n'.join(paragraphs[1:])
        else:
            logger.warning("Not enough paragraphs, using full text as summary")
            summary = full_text
            article_text = ""

        return summary, article_text

    @staticmethod
    def _validate_article(summary: str, article: str) -> None:
        """Validates the generated article"""
        if not summary and not article:
            raise ArticleGenerationException("Generated article is empty")

        if len(summary) < 10:
            logger.warning(f"Summary is too short: {len(summary)} chars")

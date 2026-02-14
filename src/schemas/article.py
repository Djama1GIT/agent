from pydantic import BaseModel, Field


class ArticleSchema(BaseModel):
    """Article Schema.

    Represents an article with its full content and a generated summary.
    This model is used for storing and validating article data.

    Attributes:
        summary: A concise summary or abstract of the article content.
                Should capture the main points of the full article.
        article: The complete, full-text content of the article.
                Contains all the detailed information and context.

    Example:
        >>> article = ArticleSchema(
        ...     summary="This article discusses the impact of AI on modern healthcare...",
        ...     article="Artificial intelligence is revolutionizing healthcare... (full text)"
        ... )
        >>> print(article.summary)
        This article discusses the impact of AI on modern healthcare...
    """
    summary: str = Field(
        ...,
        description="Generated summary or abstract of the article content",
        examples=["Brief overview of the article's main points..."]
    )
    article: str = Field(
        ...,
        description="Full text content of the article",
        examples=["Complete article text with all details..."]
    )
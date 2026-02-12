from pydantic import BaseModel


class ArticleSchema(BaseModel):
    summary: str
    article: str

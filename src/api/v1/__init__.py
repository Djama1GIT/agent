from fastapi import APIRouter
from src.api.v1.agent import router as v1_agent_router
from src.api.v1.article import router as v1_article_router

v1_router = APIRouter()

v1_router.include_router(v1_agent_router)
v1_router.include_router(v1_article_router)

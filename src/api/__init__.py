from fastapi import APIRouter

from src.api.v1 import v1_router

main_api_router = APIRouter()
main_api_router.include_router(v1_router, prefix='/v1')
main_api_router.include_router(v1_router, include_in_schema=False)
main_api_router.include_router(v1_router, prefix='/latest', include_in_schema=False)


@main_api_router.get("/health")
async def health_check():
    return {"status": "ok"}

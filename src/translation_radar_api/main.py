from fastapi import FastAPI

from translation_radar_api.config import settings
from translation_radar_api.routes.alerts import router as alerts_router
from translation_radar_api.routes.health import router as health_router
from translation_radar_api.routes.rag import router as rag_router
from translation_radar_api.routes.sources import router as sources_router


app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(health_router)
app.include_router(alerts_router)
app.include_router(rag_router)
app.include_router(sources_router)
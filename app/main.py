from fastapi import FastAPI
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging

s = get_settings()
configure_logging(s.log_level)

app = FastAPI(title=s.app_name, version="0.1.0")
app.include_router(router)
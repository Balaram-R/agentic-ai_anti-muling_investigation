from collections.abc import Generator
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from app.core.config import get_settings
@lru_cache
def get_engine(): return create_engine(get_settings().database_url,pool_pre_ping=True)
@lru_cache
def get_factory(): return sessionmaker(bind=get_engine(),autoflush=False,expire_on_commit=False)
def SessionLocal(): return get_factory()()
def get_db()->Generator[Session,None,None]:
    db=SessionLocal()
    try: yield db
    finally: db.close()

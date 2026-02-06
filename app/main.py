from fastapi import FastAPI, Depends
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from core.base_response import ApiResponse, BusinessException, ErrorCode
from core.middleware import ResponseMiddleware
from core.exception_handler import create_exception_handlers
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from services.strategy_service import StrategyService
from db.deps import get_catalog_db, get_user_db, get_insight_db
from core.config import settings
app = FastAPI(
    title="Chord AI Insight API",
    description="Chord AI Insight 서비스 API 문서",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ResponseMiddleware)
create_exception_handlers(app)

@app.get("/root")
async def read_root(catalog_db: Session = Depends(get_catalog_db), user_db: Session = Depends(get_user_db), insight_db: Session = Depends(get_insight_db)):
    service = StrategyService(catalog_db, user_db, insight_db)
    await service.create_strategy()  
    return "hi"

def main():
    print("Starting Chord AI Insight API...")


if __name__ == "__main__":
    main()

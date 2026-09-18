from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.common.database import engine, get_db
from app.common.response import ApiResponse
from app.common.exceptions import register_exception_handlers
from app.auth.router import router as auth_router
from app.user.router import router as user_router
from app.files.router import UPLOAD_DIR, router as file_router
from app.modules.ride.router import router as ride_router
from app.modules.quest.router import router as quest_router
from app.modules.book.router import router as book_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield
    engine.dispose()


app = FastAPI(title='CampusLink API', version='0.2.0', lifespan=lifespan)
register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(file_router)
app.include_router(ride_router)
app.include_router(quest_router)
app.include_router(book_router)
app.mount('/uploads', StaticFiles(directory=UPLOAD_DIR, check_dir=False), name='uploads')


class HealthData(BaseModel):
    status: str = 'ok'


@app.get(
    '/api/health',
    response_model=ApiResponse[HealthData],
    responses={503: {'model': ApiResponse[None], 'description': 'Database unavailable'}},
    tags=['health'],
)
def health(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(text('SELECT 1')).scalar_one()
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={'code': 503, 'message': '数据库暂时不可用', 'data': None},
        )
    return ApiResponse(data=HealthData())

from fastapi import APIRouter

from app.auth import service
from app.auth.dependencies import DatabaseSession
from app.auth.schemas import Credentials, RegisterRequest, TokenResponse
from app.common.response import ApiResponse
from app.user.schemas import UserPublic

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/register', response_model=ApiResponse[UserPublic], summary='注册账号')
def register(payload: RegisterRequest, db: DatabaseSession):
    return ApiResponse(data=UserPublic.model_validate(service.register(db, payload)))


@router.post('/login', response_model=ApiResponse[TokenResponse], summary='登录并获取访问令牌')
def login(payload: Credentials, db: DatabaseSession):
    return ApiResponse(data=service.login(db, payload))

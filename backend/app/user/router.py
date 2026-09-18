from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, DatabaseSession
from app.common.response import ApiResponse
from app.user.schemas import UserPublic, UserUpdate
from app.user.service import update_profile

router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('/me', response_model=ApiResponse[UserPublic], summary='获取当前用户资料')
def get_me(user: CurrentUser):
    return ApiResponse(data=UserPublic.model_validate(user))


@router.put('/me', response_model=ApiResponse[UserPublic], summary='更新当前用户资料',
            description='只更新提交的字段；昵称不能为空，头像传 null 表示清空。')
def update_me(payload: UserUpdate, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=UserPublic.model_validate(update_profile(db, user, payload)))

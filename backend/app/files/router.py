import warnings
from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser
from app.common.config import BACKEND_DIR
from app.common.response import ApiResponse

UPLOAD_DIR = BACKEND_DIR / 'uploads'
MAX_FILE_SIZE = 5 * 1024 * 1024
EXTENSIONS = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}
router = APIRouter(prefix='/api/files', tags=['files'])


class UploadedFile(BaseModel):
    url: str


@router.post('/upload', response_model=ApiResponse[UploadedFile], summary='上传图片',
             description='需要登录；multipart 字段 file；JPEG、PNG、WebP，最大 5 MiB。返回 URL 后由调用方保存关联。')
def upload_image(user: CurrentUser, file: UploadFile):
    try:
        content = file.file.read(MAX_FILE_SIZE + 1)
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(413, '图片不能超过 5 MB')
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as picture:
                extension = EXTENSIONS.get(picture.format)
                if extension is None:
                    raise HTTPException(415, '仅支持 JPEG、PNG、WebP 图片')
                picture.verify()
            with Image.open(BytesIO(content)) as picture:
                picture.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise HTTPException(415, '图片无效或尺寸过大，请换一张图片') from None
    finally:
        file.file.close()

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f'{uuid4().hex}.{extension}'
    (UPLOAD_DIR / filename).write_bytes(content)
    return ApiResponse(data=UploadedFile(url=f'/uploads/{filename}'))

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


def error_response(status: int, message: str, headers=None):
    return JSONResponse(
        status_code=status, content={'code': status, 'message': message, 'data': None},
        headers=headers,
    )


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return error_response(exc.status_code, str(exc.detail), exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Validation errors may contain passwords; never serialize input values.
        fields = sorted({str(error['loc'][-1]) for error in exc.errors() if error['loc']})
        suffix = f"（{', '.join(fields)}）" if fields else ''
        return error_response(422, f'请求参数不符合要求{suffix}')

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.error('Unhandled API error: %s', type(exc).__name__)
        return error_response(500, '服务暂时不可用，请稍后重试')
